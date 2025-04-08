package controller

import (
    "fmt"
    "github.com/xushneg6/crackmes.one/app/model"
    "github.com/xushneg6/crackmes.one/app/shared/recaptcha"
    "github.com/xushneg6/crackmes.one/app/shared/session"
    "github.com/xushneg6/crackmes.one/app/shared/view"
    "log"
    "net/http"

    "github.com/gorilla/context"
    "github.com/julienschmidt/httprouter"
    "github.com/kennygrant/sanitize"
)

func LeaveCommentPOST(w http.ResponseWriter, r *http.Request) {
	// Get session
	sess := session.Instance(r)
	var err error
	var params httprouter.Params
	params = context.Get(r, "params").(httprouter.Params)
	crackmehexid := params.ByName("hexid")

	// Validate with required fields
	if validate, missingField := view.Validate(r, []string{"comment"}); !validate {
		sess.AddFlash(view.Flash{"Field missing: " + missingField, view.FlashError})
		sess.Save(r, w)
		CrackMeGET(w, r)
		return
	}

	if !recaptcha.Verified(r) {
		sess.AddFlash(view.Flash{"reCAPTCHA invalid!", view.FlashError})
		sess.Save(r, w)
		CrackMeGET(w, r)
		return
	}

	username := fmt.Sprintf("%s", sess.Values["name"])
	comment := r.FormValue("comment")

	comment = sanitize.HTML(comment)

	err = model.CommentCreate(comment, username, crackmehexid)

	if err != nil {
		log.Println(err)
		sess.AddFlash(view.Flash{"Comment creation failed. Please try again later.", view.FlashError})
		sess.Save(r, w)
		CrackMeGET(w, r)
		return
	}

	crackme, err := model.CrackmeByHexId(crackmehexid)
	if err == nil && crackme.Author != username {
		err = model.NotificationAdd(crackme.Author, "New comment on your crackme '"+
			crackme.Name+"' by: "+username)
		if err != nil {
			log.Println(err)
		}
	} else {
		log.Println(err)
	}

	sess.AddFlash(view.Flash{"Comment uploaded!", view.FlashSuccess})
	sess.Save(r, w)
	http.Redirect(w, r, "/crackme/"+crackmehexid, http.StatusFound)
	return
}
