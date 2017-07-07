defmodule Minigrade.Router do
  use Minigrade.Web, :router

  pipeline :browser do
    plug :accepts, ["html"]
    plug :fetch_session
    plug :fetch_flash
    plug :protect_from_forgery
    plug :put_secure_browser_headers
  end

  pipeline :api do
    plug :accepts, ["json"]
  end

  scope "/", Minigrade do
    pipe_through :browser # Use the default browser stack

    get "/", PageController, :index
    get "/about", AboutController, :index
    resources "/assignments", AssignmentController, only: [:index, :show]
  end

  scope "/admin", Minigrade.Admin, as: :admin do
    pipe_through :browser

    resources "/assignments", AssignmentController
  end

  # Other scopes may use custom stacks.
  # scope "/api", Minigrade do
  #   pipe_through :api
  # end
end
