package controller

import (
    "log"
    "net/http"
    "github.com/crackmesone/crackmes.one/app/model"
    "github.com/crackmesone/crackmes.one/app/shared/passhash"
    "github.com/crackmesone/crackmes.one/app/shared/recaptcha"
    "github.com/crackmesone/crackmes.one/app/shared/session"
    "github.com/crackmesone/crackmes.one/app/shared/view"
    "github.com/josephspurrier/csrfbanana"
    "strings"
)

// RegisterGET displays the register page
func RegisterGET(w http.ResponseWriter, r *http.Request) {
    // Get session
    sess := session.Instance(r)

    // Display the view
    v := view.New(r)
    v.Name = "register/register"
    v.Vars["token"] = csrfbanana.Token(w, r, sess)
    // Refill any form fields
    view.Repopulate([]string{"name", "email"}, r.Form, v.Vars)
    v.Render(w)
}

// RegisterPOST handles the registration form submission
func RegisterPOST(w http.ResponseWriter, r *http.Request) {
    // Get session
    sess := session.Instance(r)

    // Prevent brute force login attempts by not hitting MySQL and pretending like it was invalid :-)
    if sess.Values["register_attempt"] != nil && sess.Values["register_attempt"].(int) >= 5 {
        log.Println("Brute force register prevented")
        http.Redirect(w, r, "/register", http.StatusFound)
        return
    }

    // Validate with required fields
    if validate, missingField := view.Validate(r, []string{"name", "email", "password"}); !validate {
        sess.AddFlash(view.Flash{"Field missing: " + missingField, view.FlashError})
        sess.Save(r, w)
        RegisterGET(w, r)
        return
    }

    // Validate with Google reCAPTCHA
    if !recaptcha.Verified(r) {
        sess.AddFlash(view.Flash{"reCAPTCHA invalid!", view.FlashError})
        sess.Save(r, w)
        RegisterGET(w, r)
        return
    }

    // Get form values
    name := r.FormValue("name")
    email := strings.ToLower(r.FormValue("email"))
    password, errp := passhash.HashString(r.FormValue("password"))

    if (!view.AuthorizedCharsOnly(name) || !view.AuthorizedCharsOnly(email)){
        sess.AddFlash(view.Flash{"Non allowed chars", view.FlashError})
        sess.Save(r, w)
        RegisterGET(w, r)
        return
    }

    // If password hashing failed
    if errp != nil {
        log.Println(errp)
        sess.AddFlash(view.Flash{"An error occurred on the server. Please try again later.", view.FlashError})
        sess.Save(r, w)
        http.Redirect(w, r, "/register", http.StatusFound)
        return
    }

    // Get database result
    _, errmail := model.UserByMail(email)
    if errmail != model.ErrNoResult {
        //log.Println(errmail)
        sess.AddFlash(view.Flash{"Account already exists for: " + email, view.FlashError})
        sess.Save(r, w)
    } else {
        _, err := model.UserByName(name)

        if err == model.ErrNoResult { // If success (no user exists with that email)
            ex := model.UserCreate(name, email, password)
            // Will only error if there is a problem with the query
            if ex != nil {
                log.Println(ex)
                sess.AddFlash(view.Flash{"An error occurred on the server. Please try again later.", view.FlashError})
                sess.Save(r, w)
            } else {
                sess.AddFlash(view.Flash{"Account created successfully for: " + name, view.FlashSuccess})
                sess.Save(r, w)
                http.Redirect(w, r, "/login", http.StatusFound)
                return
            }
        } else if err != nil { // Catch all other errors
            log.Println(err)
            sess.AddFlash(view.Flash{"An error occurred on the server. Please try again later.", view.FlashError})
            sess.Save(r, w)
        } else { // Else the user already exists
            sess.AddFlash(view.Flash{"Account already exists for: " + name, view.FlashError})
            sess.Save(r, w)
        }
    }
    // Display the page
    RegisterGET(w, r)
}
