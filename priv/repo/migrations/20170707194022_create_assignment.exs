defmodule Minigrade.Repo.Migrations.CreateAssignment do
  use Ecto.Migration

  def change do
    create table(:assignments) do
      add :name, :string
      add :description, :string
      add :submission_files, {:array, :string}

      timestamps()
    end

  end
end
