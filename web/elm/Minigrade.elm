module Minigrade exposing (..)

import Html exposing (text, Html, div)
import Html.Attributes exposing (class)

-- Parts of every page
import Components.Common.Header as Header
import Components.Common.Footer as Footer

{-- 
  Create assignment, Modify assignment, Submit solution to assignment, View
  assignments
--}
import Components.Assignment as Assignment

{-- 
  View all grades for all students, View all grades for one student, View grade
  for one assignment and all students, view grade for one assignment and one
  student, Edit grades
--}
import Components.Grades as Grades

-- Create class, Modify class, View classes
import Components.Admin as Admin

main : Html a 
main = 
  div [ class "minigrade-app" ] [
    div [ class "minigrade-header" ] [ Header.view ],
    div [ class "minigrade-content" ] []
    ]
