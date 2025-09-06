package controller

import (
    "github.com/crackmesone/crackmes.one/app/shared/view"
    "net/http"
)


func SolutionRulesGET(w http.ResponseWriter, r *http.Request) {
    v := view.New(r)
    v.Name = "rules/solutionrules"
    v.Render(w)
}