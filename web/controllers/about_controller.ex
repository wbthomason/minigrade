defmodule Minigrade.AboutController do
  use Minigrade.Web, :controller

  def index(conn, _params) do
    render conn, "index.html"
  end
end
