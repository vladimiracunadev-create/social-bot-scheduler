(ns receiver.core
  "==================================================================================================
   RECEPTOR CLOJURE/RING + XTDB (Case 19: F# -> n8n -> Clojure (Ring) + XTDB)
   ==================================================================================================
   Paradigma funcional puro sobre la JVM. XTDB es una base de datos **bitemporal e inmutable**:
   cada `put` añade una versión (nunca sobrescribe), consultable por tiempo de validez y de
   transacción. Aquí corre **embebida in-process** (nodo in-memory), sin contenedor de BD separado.

   Cumple el contrato REST homogéneo del laboratorio: /webhook, /errors, /logs, /health, /."
  (:require [ring.adapter.jetty :as jetty]
            [cheshire.core :as json]
            [clojure.java.io :as io]
            [xtdb.api :as xt])
  (:gen-class))

;; Nodo XTDB in-memory (bitemporal). IMPORTANTE: `delay` evita arrancar la BD durante la
;; compilación AOT (`lein uberjar` evalúa las formas top-level). El nodo se crea en tiempo de
;; ejecución al forzar el delay en -main.
(defonce node (delay (xt/start-node {})))

(defn json-resp [status body]
  {:status status
   :headers {"Content-Type" "application/json"}
   :body (json/generate-string body)})

(defn handle-webhook [req]
  (let [m (json/parse-string (slurp (:body req)) true)
        id (:id m)
        text (:text m)]
    (if (or (nil? id) (nil? text) (= "" id) (= "" text))
      (json-resp 422 {:ok false :error "id y text son obligatorios"})
      (let [tx (xt/submit-tx @node [[::xt/put {:xt/id id
                                               :text text
                                               :channel (or (:channel m) "default")
                                               :created-at (System/currentTimeMillis)}]])]
        (xt/await-tx @node tx)
        (println "Post persistido en XTDB:" id)
        (json-resp 200 {:ok true
                        :message "Post persistido en XTDB (bitemporal)"
                        :case "19-fsharp-to-clojure"})))))

(defn recent-logs []
  (let [db (xt/db @node)
        rows (xt/q db '{:find [id ch txt ca]
                        :where [[e :xt/id id]
                                [e :text txt]
                                [e :channel ch]
                                [e :created-at ca]]})]
    (->> rows
         (sort-by #(nth % 3) >)
         (take 20)
         (mapv (fn [[id ch txt ca]]
                 (str "[" ca "] XTDB | id=" id " | channel=" ch " | text=" txt))))))

(defn dashboard-html []
  (if (.exists (io/file "public/index.html"))
    (slurp "public/index.html")
    "<h1>Dashboard no encontrado</h1>"))

(defn handler [req]
  (let [uri (:uri req)
        method (:request-method req)]
    (cond
      (= uri "/health")
      (json-resp 200 {:ok true :engine "xtdb"})

      (and (= uri "/webhook") (= method :post))
      (handle-webhook req)

      (and (= uri "/errors") (= method :post))
      (do (println "Error en DLQ:" (slurp (:body req)))
          (json-resp 200 {:ok true :message "Error registrado en DLQ"}))

      (= uri "/logs")
      (json-resp 200 {:ok true :logs (recent-logs)})

      (= uri "/")
      {:status 200 :headers {"Content-Type" "text/html"} :body (dashboard-html)}

      :else
      (json-resp 404 {:ok false :error "not found"}))))

(defn -main [& _]
  (force node) ; arranca XTDB en runtime (no en compilación)
  (let [port (Integer/parseInt (or (System/getenv "PORT") "8080"))]
    (println "Receiver Case 19 (Clojure/Ring + XTDB) escuchando en :" port)
    (jetty/run-jetty handler {:port port :join? true})))
