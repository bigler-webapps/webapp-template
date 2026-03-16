import React from "react";

import { Navigate } from "react-router-dom";

const UserManagementPage = () => <Navigate to="/account?tab=users" replace />;

export default UserManagementPage;
