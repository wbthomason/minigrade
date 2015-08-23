defmodule Minigrade.Repo.Migrations.CreateAssignment do
  use Ecto.Migration

  def change do
    create table(:assignments) do
      add :name, :string
      add :description, :text
      add :points, :float
      add :open, :boolean, default: false
      add :build, :string
      add :test, :string
      add :course, references(:courses)

      timestamps
    end
    create index(:assignments, [:course])

  end
end
