import React, { useEffect, useState } from "react";
import api from "../../api/axios";
import { setAccessToken, clearSession, getAccessToken, getStoredUser, getRefreshPromise, setRefreshPromise } from "../../utils/security";
import PageLoader from "../common/PageLoader";

export default function AuthInitializer({ children }) {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = getAccessToken();
    const user = getStoredUser();

    if (token) {
      setReady(true);
      return;
    }

    if (!user) {
      clearSession();
      setReady(true);
      return;
    }

    let promise = getRefreshPromise();
    if (!promise) {
      promise = api
        .post("/auth/refresh", null, {
          __isRefreshRequest: true,
        })
        .finally(() => setRefreshPromise(null));
      setRefreshPromise(promise);
    }
    promise
      .then(({ data }) => {
        if (data?.access_token) {
          setAccessToken(data.access_token);
          if (data.usuario) {
            localStorage.setItem("user", JSON.stringify(data.usuario));
          }
        } else {
          clearSession();
        }
      })
      .catch(() => {
        clearSession();
      })
      .finally(() => {
        setReady(true);
      });
  }, []);

  if (!ready) {
    return <PageLoader label="Restaurando sesión..." />;
  }

  return children;
}
