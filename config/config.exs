# This file is responsible for configuring your application
# and its dependencies with the aid of the Mix.Config module.
#
# This configuration file is loaded before any dependency and
# is restricted to this project.
use Mix.Config

# General application configuration
config :minigrade,
  ecto_repos: [Minigrade.Repo]

# Configures the endpoint
config :minigrade, Minigrade.Endpoint,
  url: [host: "localhost"],
  secret_key_base: "zx3M/buH9gPSgqOIlLByEGf4AP16jJCW3movWwhBiRdEv4BT+MHx3L+Lk/KLGebu",
  render_errors: [view: Minigrade.ErrorView, accepts: ~w(html json)],
  pubsub: [name: Minigrade.PubSub,
           adapter: Phoenix.PubSub.PG2]

# Configures Elixir's Logger
config :logger, :console,
  format: "$time $metadata[$level] $message\n",
  metadata: [:request_id]

# Import environment specific config. This must remain at the bottom
# of this file so it overrides the configuration defined above.
import_config "#{Mix.env}.exs"
