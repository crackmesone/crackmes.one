package controller

import (
    "github.com/xusheng6/crackmes.one/app/shared/session"
    "github.com/xusheng6/crackmes.one/app/shared/view"
    "net/http"

    "github.com/josephspurrier/csrfbanana"
)


func SolutionRulesGET(w http.ResponseWriter, r *http.Request) {
    sess := session.Instance(r)

    v := view.New(r)
    v.Name = "rules/solutionrules" 
    v.Vars["token"] = csrfbanana.Token(w, r, sess)
    
    v.Render(w)
    sess.Save(r, w)
}