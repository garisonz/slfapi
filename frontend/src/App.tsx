import { Link, Navigate, Route, Routes } from "react-router";
import { useAuth } from "./auth/AuthContext";
import { ProtectedRoute } from "./auth/ProtectedRoute";
import Navbar from "./components/Navbar";
import AccountPage from "./pages/AccountPage";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";

function App() {
  const { user } = useAuth();

  return (
    <>
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<Navigate to={user ? "/dashboard" : "/login"} replace />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/account" element={<AccountPage />} />
          </Route>
          <Route path="*" element={
            <section>
              <h1>Page not found</h1>
              <Link to={user ? "/dashboard" : "/login"}>Go to your home page</Link>
            </section>
          } />
        </Routes>
      </main>
    </>
  );
}

export default App;
