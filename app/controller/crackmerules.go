package controller

import (
	"net/http"

	"github.com/crackmesone/crackmes.one/app/shared/view"
)

func CrackmeRulesGET(w http.ResponseWriter, r *http.Request) {
	v := view.New(r)
	v.Name = "rules/crackmerules"
	v.Render(w)
}
