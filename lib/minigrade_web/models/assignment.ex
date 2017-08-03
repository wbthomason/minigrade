defmodule MinigradeWeb.Assignment do
  use Minigrade.Web, :model

  schema "assignments" do
    field :name, :string
    field :description, :string
    field :submission_files, {:array, :string}

    timestamps()
  end

  @doc """
  Builds a changeset based on the `struct` and `params`.
  """
  def changeset(struct, params \\ %{}) do
    struct
    |> cast(params, [:name, :description, :submission_files])
    |> validate_required([:name, :description, :submission_files])
  end
end
