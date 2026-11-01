(defproject case19-receiver "1.0.0"
  :description "Case 19 — receptor Clojure/Ring con XTDB embebido (bitemporal)."
  :dependencies [[org.clojure/clojure "1.12.0"]
                 ;; ring 1.15.x sube el adaptador de Jetty 11 a Jetty 12.1.14 y con eso
                 ;; salen de la imagen CVE-2024-7708, CVE-2024-8184 y CVE-2026-6790.
                 [ring/ring-core "1.15.6"]
                 [ring/ring-jetty-adapter "1.15.6"]
                 [cheshire "6.2.0"]
                 ;; cheshire 6.2.0 trae jackson-core 2.21.1: lo pisamos a 2.21.8 por
                 ;; CVE-2026-89425, CVE-2026-89407 y CVE-2026-68494.
                 [com.fasterxml.jackson.core/jackson-core "2.21.8"]
                 ;; XTDB 1.24.3 se mantiene: sin advisory y la rama 2.x es una reescritura.
                 [com.xtdb/xtdb-core "1.24.3"]]
  :main ^:skip-aot receiver.core
  :aot [receiver.core]
  :uberjar-name "receiver-standalone.jar"
  :profiles {:uberjar {:aot :all}})
