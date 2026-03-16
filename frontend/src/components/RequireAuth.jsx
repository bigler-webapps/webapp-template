import React, { useContext } from "react";

import { Box, CircularProgress } from "@mui/material";
import { AuthContext } from "@micha.bigler/ui-core-micha";
import { Navigate, useLocation } from "react-router-dom";

const RequireAuth = ({ children }) => {
  const { loading, user } = useContext(AuthContext);
  const location = useLocation();

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!user) {
    return <Navigate replace state={{ from: location }} to="/login" />;
  }

  return children;
};

export default RequireAuth;
