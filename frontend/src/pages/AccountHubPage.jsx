import React, { useContext } from "react";

import { AccountPage, AuthContext } from "@micha.bigler/ui-core-micha";
import { Navigate } from "react-router-dom";

const AccountHubPage = () => {
  const { user } = useContext(AuthContext);

  if (user?.is_new) {
    return <Navigate to="/welcome" replace />;
  }

  return <AccountPage />;
};

export default AccountHubPage;
