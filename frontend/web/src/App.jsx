import Navbar from "./components/navbar.jsx";
import {useEffect, useState} from "react";
import {Routes, Route, Navigate} from 'react-router-dom'
import {apiRequest, loadTokensFromStorage, setTokens} from "./services/apiService.js";


function App() {
    const [currentUser, setCurrentUser] = useState(null)

    useEffect(()=>{
        const tokens =loadTokensFromStorage()
        if (tokens) {
            apiRequest("auth/me/")
                .then((user) => setCurrentUser(user))
                .catch(() => {
                    setTokens(null);
                    setCurrentUser(null);
                });
        }

    }, [])

    const logout = ()=>{
        setCurrentUser(null)
    }

    return (
        <>
            {/*<Navbar currentUser={}/>*/}

            <Routes>
                <Route
                    path="/"
                />
            </Routes>
        </>
    )
}

export default App
