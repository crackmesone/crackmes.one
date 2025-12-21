package controller

import (
    "github.com/crackmesone/crackmes.one/app/model"
    "log"
    "net/http"
    "sort"
    //"app/shared/session"
    "github.com/crackmesone/crackmes.one/app/shared/view"

    "fmt"
    "github.com/gorilla/context"
    "github.com/julienschmidt/httprouter"
    "github.com/crackmesone/crackmes.one/app/shared/session"
)

type By func(p1, p2 *model.User) bool

func (by By) Sort(users []model.User) {
    ps := &userSorter{
        users: users,
        by:    by, // The Sort method's receiver is the function (closure) that defines the sort order.
    }
    sort.Sort(ps)
}

type userSorter struct {
    users []model.User
    by    func(p1, p2 *model.User) bool // Closure used in the Less method.
}

func (s *userSorter) Len() int {
    return len(s.users)
}

// Swap is part of sort.Interface.
func (s *userSorter) Swap(i, j int) {
    s.users[i], s.users[j] = s.users[j], s.users[i]
}

// Less is part of sort.Interface. It is implemented by calling the "by" closure in the sorter.
func (s *userSorter) Less(i, j int) bool {
    return s.by(&s.users[i], &s.users[j])
}

// NotepadReadGET displays the notes in the notepad
func UserGET(w http.ResponseWriter, r *http.Request) {
    var params httprouter.Params
    params = context.Get(r, "params").(httprouter.Params)
    name := params.ByName("name")

    user, err := model.UserByName(name)
    if err != nil {
        log.Println(err)
        Error404(w, r)
        return
    }

    // Use the actual username from the database for subsequent lookups
    // This ensures case-insensitive lookup works while maintaining data consistency
    actualUsername := user.Name

    crackmes, err := model.CrackmesByUser(actualUsername)
    if err != nil {
        log.Println(err)
        Error500(w, r)
        return
    }

    nbCrackmes, err := model.CountCrackmesByUser(actualUsername)
    if err != nil {
        log.Println(err)
        Error500(w, r)
        return
    }

    nbSolutions, err := model.CountSolutionsByUser(actualUsername)
    if err != nil {
        log.Println(err)
        Error500(w, r)
        return
    }

    nbComments, err := model.CountCommentsByUser(actualUsername)
    if err != nil {
        log.Println(err)
        Error500(w, r)
        return
    }

    solutions, err := model.SolutionsByUser(actualUsername)
    if err != nil {
        log.Println(err)
        Error500(w, r)
        return
    }

    comments, err := model.CommentsByUser(actualUsername)
    if err != nil {
        log.Println(err)
        Error500(w, r)
        return
    }

    solutionsext := make([]model.SolutionExtended, len(solutions))

    for i := range solutions {
        solutionsext[i].Solution = &solutions[i]
        solutionsext[i].Crackmeshexid = (&solutions[i]).CrackmeId.Hex()
        tmpcrackme, err := model.CrackmeByHexId(solutionsext[i].Crackmeshexid)
        if err != nil {
            log.Println(err)
            Error500(w, r)
            return
        }
        solutionsext[i].Crackmename = tmpcrackme.Name
    }

    // NbComments and NbSolutions for each CRACKME are stored in the database
    // and are retrieved directly from the crackme documents.
    // Note: User.NbSolutions and User.NbComments (for the USER) are still
    // calculated dynamically and NOT stored in the database.

    // Determine if the user is viewing their own profile page
    sess := session.Instance(r)
    sessionUsername := ""
    if sess.Values["name"] != nil {
        sessionUsername = fmt.Sprintf("%s", sess.Values["name"])
    }
    viewingOwnPage := sessionUsername != "" && sessionUsername == actualUsername

    user.NbCrackmes = nbCrackmes
    user.NbSolutions = nbSolutions
    user.NbComments = nbComments

    // Display the view
    v := view.New(r)
    v.Name = "user/read"
    v.Vars["username"] = user.Name
    v.Vars["NbCrackmes"] = user.NbCrackmes
    v.Vars["NbSolutions"] = user.NbSolutions
    v.Vars["NbComments"] = user.NbComments
    v.Vars["crackmes"] = crackmes
    v.Vars["solutions"] = solutionsext
    v.Vars["comments"] = comments
    v.Vars["viewingOwnPage"] = viewingOwnPage
    v.Render(w)
}

func UsersGET(w http.ResponseWriter, r *http.Request) {

    users, err := model.AllUsersVisible()
    name := func(p1, p2 *model.User) bool {
        return p1.Name < p2.Name
    }
    By(name).Sort(users)

    if err != nil {
        log.Println(err)
        Error500(w, r)
        return
    }

    for _, user := range users {
        nbSolutions, err := model.CountSolutionsByUser(user.Name)
        if err != nil {
            log.Println(err)
            Error500(w, r)
            return
        }

        nbComments, err := model.CountCommentsByUser(user.Name)
        if err != nil {
            log.Println(err)
            Error500(w, r)
            return
        }
        nbCrackmes, err := model.CountCrackmesByUser(user.Name)
        if err != nil {
            log.Println(err)
            Error500(w, r)
            return
        }
        user.NbSolutions = nbSolutions
        user.NbComments = nbComments
        user.NbCrackmes = nbCrackmes
    }
    // Display the view
    v := view.New(r)
    v.Name = "users/read"
    v.Vars["users"] = users
    v.Render(w)
}
