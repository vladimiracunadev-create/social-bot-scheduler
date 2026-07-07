defmodule Case11Origin.MixProject do
  use Mix.Project

  def project do
    [
      app: :case11_origin,
      version: "1.0.0",
      elixir: "~> 1.17",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  # Sin dependencias externas: usamos :httpc (inets) para HTTP y el módulo :json de OTP 27.
  def application do
    [extra_applications: [:logger, :inets, :ssl]]
  end

  defp deps, do: []
end
