//
//      Copyright (C) 2012 DataStax Inc.
//
//   Licensed under the Apache License, Version 2.0 (the "License");
//   you may not use this file except in compliance with the License.
//   You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
//   Unless required by applicable law or agreed to in writing, software
//   distributed under the License is distributed on an "AS IS" BASIS,
//   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//   See the License for the specific language governing permissions and
//   limitations under the License.
//
using System;
using System.Collections.Generic;

namespace Cassandra
{
    /// <summary>
    ///  Informations and known state of a Cassandra cluster. <p> This is the main
    ///  entry point of the driver. A simple example of access to a Cassandra cluster
    ///  would be:
    /// <pre> Cluster cluster = Cluster.Builder.AddContactPoint("192.168.0.1").Build();
    ///  Session session = Cluster.Connect("db1");
    ///  foreach (var row in session.execute("SELECT * FROM table1"))
    ///    //do something ... </pre>
    ///  </p><p> A cluster object maintains a
    ///  permanent connection to one of the cluster node that it uses solely to
    ///  maintain informations on the state and current topology of the cluster. Using
    ///  the connection, the driver will discover all the nodes composing the cluster
    ///  as well as new nodes joining the cluster.</p>
    /// </summary>
    public class Cluster : IDisposable
    {
        private readonly Logger _logger = new Logger(typeof(Cluster));
        private readonly IEnumerable<IPAddress> _contactPoints;
        private readonly Configuration _configuration;

        private Cluster(IEnumerable<IPAddress> contactPoints, Configuration configuration)
        {
            this._contactPoints = contactPoints;
            this._configuration = configuration;
            this._metadata = new Metadata(configuration.Policies.ReconnectionPolicy);

            var controlpolicies = new Cassandra.Policies(
                //new ControlConnectionLoadBalancingPolicy(_configuration.Policies.LoadBalancingPolicy),
                _configuration.Policies.LoadBalancingPolicy,
                new ExponentialReconnectionPolicy(2 * 1000, 5 * 60 * 1000),
                Cassandra.Policies.DefaultRetryPolicy);
        }
    }
}