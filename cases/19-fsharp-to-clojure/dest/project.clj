(defproject case19-receiver "1.0.0"
  :description "Case 19 — receptor Clojure/Ring con XTDB embebido (bitemporal)."
  :dependencies [[org.clojure/clojure "1.11.4"]
                 [ring/ring-core "1.12.2"]
                 [ring/ring-jetty-adapter "1.12.2"]
                 [cheshire "5.13.0"]
                 [com.xtdb/xtdb-core "1.24.3"]]
  :main ^:skip-aot receiver.core
  :aot [receiver.core]
  :uberjar-name "receiver-standalone.jar"
  :profiles {:uberjar {:aot :all}})
