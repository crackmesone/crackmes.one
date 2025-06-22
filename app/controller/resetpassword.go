package controller

import (
	"github.com/josephspurrier/csrfbanana"
	"github.com/xusheng6/crackmes.one/app/shared/session"
	"github.com/xusheng6/crackmes.one/app/shared/view"
	"log"
	"net/http"

	"github.com/xusheng6/crackmes.one/app/model"
	"github.com/xusheng6/crackmes.one/app/shared/passhash"
)

// ResetPasswordWithCurrentGET renders the password reset page.
func ResetPasswordWithCurrentGET(w http.ResponseWriter, r *http.Request) {
	// Get session
	sess := session.Instance(r)

	// Display the view
	v := view.New(r)
	v.Name = "user/change-password"
	v.Vars["token"] = csrfbanana.Token(w, r, sess)
	v.Render(w)
	sess.Save(r, w)
}

// ResetPasswordWithCurrentPOST allows users to reset their password after verifying the current password.
func ResetPasswordWithCurrentPOST(w http.ResponseWriter, r *http.Request) {
	// Get session and username
	sess := session.Instance(r)
	username, ok := sess.Values["name"].(string)
	if !ok || username == "" {
		// Handle the case where the username does not exist in the session
		http.Error(w, "User not logged in or session invalid", http.StatusUnauthorized)
		return
	}

	// Parse form values
	currentPassword := r.FormValue("current_password")
	newPassword := r.FormValue("new_password")
	newPasswordVerify := r.FormValue("new_password_verify")

	// Check if new passwords are non-empty, match, and meet the criteria
	if newPassword == "" || newPasswordVerify == "" {
		http.Error(w, "New password fields cannot be empty", http.StatusBadRequest)
		return
	}
	if newPassword != newPasswordVerify {
		http.Error(w, "Passwords do not match", http.StatusBadRequest)
		return
	}
	if len(newPassword) < 8 {
		http.Error(w, "New password must be at least 8 characters long", http.StatusBadRequest)
		return
	}

	//// Regex check for allowed characters
	//allowedPasswordRegex := `^[A-Za-z0-9!@#$%^&*()_+\-=[\]{};':"|,.<>\/?]*$`
	//matched, err := regexp.MatchString(allowedPasswordRegex, newPassword)
	//if err != nil || !matched {
	//	http.Error(w, "New password contains invalid characters", http.StatusBadRequest)
	//	return
	//}

	// Fetch user info from the database
	user, err := model.UserByName(username)
	if err != nil {
		log.Println("Error: User not found:", err)
		http.Error(w, "User not found", http.StatusBadRequest)
		return
	}

	// Verify the current password
	if !passhash.MatchString(user.Password, currentPassword) {
		http.Error(w, "Current password is incorrect", http.StatusUnauthorized)
		return
	}

	// Hash the new password
	hashedNewPassword, err := passhash.HashString(newPassword)
	if err != nil {
		log.Println("Error hashing new password:", err)
		http.Error(w, "Could not hash new password", http.StatusInternalServerError)
		return
	}

	// Update the user's password in the database
	err = model.UpdateUserPassword(username, hashedNewPassword)
	if err != nil {
		log.Println("Error updating user password:", err)
		http.Error(w, "Could not update password", http.StatusInternalServerError)
		return
	}

	// Respond with success
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("Password has been successfully updated"))
}