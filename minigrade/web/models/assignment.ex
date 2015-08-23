defmodule Minigrade.Assignment do
  use Minigrade.Web, :model

  schema "assignments" do
    field :name, :string
    field :description, :string
    field :points, :float
    field :open, :boolean, default: false
    field :build, :string
    field :test, :string
    belongs_to :course, Minigrade.Course

    timestamps
  end

  @required_fields ~w(name description points open build test)
  @optional_fields ~w()

  @doc """
  Creates a changeset based on the `model` and `params`.

  If no params are provided, an invalid changeset is returned
  with no validation performed.
  """
  def changeset(model, params \\ :empty) do
    model
    |> cast(params, @required_fields, @optional_fields)
  end
end
