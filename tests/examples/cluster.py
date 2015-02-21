"""
This module houses the main classes you will interact with,
:class:`.Cluster` and :class:`.Session`.
"""
from __future__ import absolute_import

from concurrent.futures import ThreadPoolExecutor


# default to gevent when we are monkey patched, otherwise if libev is available, use that as the
# default because it's faster than asyncore
if 'gevent.monkey' in sys.modules:
    from cassandra.io.geventreactor import GeventConnection as DefaultConnection
else:
    try:
        from cassandra.io.libevreactor import LibevConnection as DefaultConnection  # NOQA
    except ImportError:
        from cassandra.io.asyncorereactor import AsyncoreConnection as DefaultConnection  # NOQA

# Forces load of utf8 encoding module to avoid deadlock that occurs
# if code that is being imported tries to import the module in a seperate
# thread.
# See http://bugs.python.org/issue10923
"".encode('utf8')

log = logging.getLogger(__name__)


DEFAULT_MIN_REQUESTS = 5
DEFAULT_MAX_REQUESTS = 100

DEFAULT_MIN_CONNECTIONS_PER_LOCAL_HOST = 2
DEFAULT_MAX_CONNECTIONS_PER_LOCAL_HOST = 8

DEFAULT_MIN_CONNECTIONS_PER_REMOTE_HOST = 1
DEFAULT_MAX_CONNECTIONS_PER_REMOTE_HOST = 2


_NOT_SET = object()


class NoHostAvailable(Exception):
    """
    Raised when an operation is attempted but all connections are
    busy, defunct, closed, or resulted in errors when used.
    """

    errors = None
    """
    A map of the form ``{ip: exception}`` which details the particular
    Exception that was caught for each host the operation was attempted
    against.
    """

    def __init__(self, message, errors):
        Exception.__init__(self, message, errors)
        self.errors = errors


def _future_completed(future):
    """ Helper for run_in_executor() """
    exc = future.exception()
    if exc:
        log.debug("Failed to run task on executor", exc_info=exc)


def run_in_executor(f):
    """
    A decorator to run the given method in the ThreadPoolExecutor.
    """

    @wraps(f)
    def new_f(self, *args, **kwargs):

        try:
            future = self.executor.submit(f, self, *args, **kwargs)
            future.add_done_callback(_future_completed)
        except Exception:
            log.exception("Failed to submit task to executor")

    return new_f


class Cluster(object):
    """
    The main class to use when interacting with a Cassandra cluster.
    Typically, one instance of this class will be created for each
    separate Cassandra cluster that your application interacts with.

    Example usage::

        >>> from cassandra.cluster import Cluster
        >>> cluster = Cluster(['192.168.1.1', '192.168.1.2'])
        >>> session = cluster.connect()
        >>> session.execute("CREATE KEYSPACE ...")
        >>> ...
        >>> cluster.shutdown()

    """

    port = 9042
    """
    The server-side port to open connections to. Defaults to 9042.
    """

    cql_version = None
    """
    If a specific version of CQL should be used, this may be set to that
    string version.  Otherwise, the highest CQL version supported by the
    server will be automatically used.
    """

    compression = True
    """
    Whether or not compression should be enabled when possible. Defaults to
    :const:`True` and attempts to use snappy compression.
    """

    auth_provider = None
    """
    An optional function that accepts one argument, the IP address of a node,
    and returns a dict of credentials for that node.
    """

    load_balancing_policy = None
    """
    An instance of :class:`.policies.LoadBalancingPolicy` or
    one of its subclasses.  Defaults to :class:`~.RoundRobinPolicy`.
    """

    reconnection_policy = ExponentialReconnectionPolicy(1.0, 600.0)
    """
    An instance of :class:`.policies.ReconnectionPolicy`. Defaults to an instance
    of :class:`.ExponentialReconnectionPolicy` with a base delay of one second and
    a max delay of ten minutes.
    """

    default_retry_policy = RetryPolicy()
    """
    A default :class:`.policies.RetryPolicy` instance to use for all
    :class:`.Statement` objects which do not have a :attr:`~.Statement.retry_policy`
    explicitly set.
    """

    conviction_policy_factory = SimpleConvictionPolicy
    """
    A factory function which creates instances of
    :class:`.policies.ConvictionPolicy`.  Defaults to
    :class:`.policies.SimpleConvictionPolicy`.
    """

    metrics_enabled = False
    """
    Whether or not metric collection is enabled.  If enabled, :attr:`.metrics`
    will be an instance of :class:`.metrics.Metrics`.
    """

    metrics = None
    """
    An instance of :class:`.metrics.Metrics` if :attr:`.metrics_enabled` is
    :const:`True`, else :const:`None`.
    """

    ssl_options = None
    """
    A optional dict which will be used as kwargs for ``ssl.wrap_socket()``
    when new sockets are created.  This should be used when client encryption
    is enabled in Cassandra.

    By default, a ``ca_certs`` value should be supplied (the value should be
    a string pointing to the location of the CA certs file), and you probably
    want to specify ``ssl_version`` as ``ssl.PROTOCOL_TLSv1`` to match
    Cassandra's default protocol.
    """

    sockopts = None
    """
    An optional list of tuples which will be used as arguments to
    ``socket.setsockopt()`` for all created sockets.
    """

    max_schema_agreement_wait = 10
    """
    The maximum duration (in seconds) that the driver will wait for schema
    agreement across the cluster. Defaults to ten seconds.
    """

    metadata = None
    """
    An instance of :class:`cassandra.metadata.Metadata`.
    """

    connection_class = DefaultConnection
    """
    This determines what event loop system will be used for managing
    I/O with Cassandra.  These are the current options:

    * :class:`cassandra.io.asyncorereactor.AsyncoreConnection`
    * :class:`cassandra.io.libevreactor.LibevConnection`

    By default, ``AsyncoreConnection`` will be used, which uses
    the ``asyncore`` module in the Python standard library.  The
    performance is slightly worse than with ``libev``, but it is
    supported on a wider range of systems.

    If ``libev`` is installed, ``LibevConnection`` will be used instead.
    """

    control_connection_timeout = 2.0
    """
    A timeout, in seconds, for queries made by the control connection, such
    as querying the current schema and information about nodes in the cluster.
    If set to :const:`None`, there will be no timeout for these queries.
    """

    sessions = None
    control_connection = None
    scheduler = None
    executor = None
    _is_shutdown = False
    _is_setup = False
    _prepared_statements = None
    _prepared_statement_lock = Lock()

    _listeners = None
    _listener_lock = None

    def __init__(self,
                 contact_points=("127.0.0.1",),
                 port=9042,
                 compression=True,
                 auth_provider=None,
                 load_balancing_policy=None,
                 reconnection_policy=None,
                 default_retry_policy=None,
                 conviction_policy_factory=None,
                 metrics_enabled=False,
                 connection_class=None,
                 ssl_options=None,
                 sockopts=None,
                 cql_version=None,
                 executor_threads=2,
                 max_schema_agreement_wait=10,
                 control_connection_timeout=2.0):
        """
        Any of the mutable Cluster attributes may be set as keyword arguments
        to the constructor.
        """
        self.contact_points = contact_points
        self.port = port
        self.compression = compression

        # let Session objects be GC'ed (and shutdown) when the user no longer
        # holds a reference. Normally the cycle detector would handle this,
        # but implementing __del__ prevents that.
        self.sessions = WeakSet()
        self.metadata = Metadata(self)
        self.control_connection = None
        self._prepared_statements = WeakValueDictionary()

    def get_core_connections_per_host(self, host_distance):
        """
        Gets the minimum number of connections per Session that will be opened
        for each host with :class:`~.HostDistance` equal to `host_distance`.
        The default is 2 for :attr:`~HostDistance.LOCAL` and 1 for
        :attr:`~HostDistance.REMOTE`.
        """
        return self._core_connections_per_host[host_distance]

    def __del__(self):
        # we don't use shutdown() because we want to avoid shutting down
        # Sessions while they are still being used (in case there are no
        # longer any references to this Cluster object, but there are
        # still references to the Session object)
        if not self._is_shutdown:
            if self.scheduler:
                self.scheduler.shutdown()
            if self.control_connection:
                self.control_connection.shutdown()
            if self.executor:
                self.executor.shutdown(wait=False)

    def _on_up_future_completed(self, host, futures, results, lock, finished_future):
        with lock:
            futures.discard(finished_future)

            try:
                results.append(finished_future.result())
            except Exception as exc:
                results.append(exc)

            if futures:
                return

        try:
            # all futures have completed at this point
            for exc in [f for f in results if isinstance(f, Exception)]:
                log.error("Unexpected failure while marking node %s up:", host, exc_info=exc)
                self._cleanup_failed_on_up_handling(host)
                return

            if not all(results):
                log.debug("Connection pool could not be created, not marking node %s up", host)
                self._cleanup_failed_on_up_handling(host)
                return

            # mark the host as up and notify all listeners
            host.set_up()
            for listener in self.listeners:
                listener.on_up(host)
        finally:
            host._handle_node_up_condition.acquire()
            if host._currently_handling_node_up:
                host._currently_handling_node_up = False
                host._handle_node_up_condition.notify()
            host._handle_node_up_condition.release()

        # see if there are any pools to add or remove now that the host is marked up
        for session in self.sessions:
            session.update_created_pools()

