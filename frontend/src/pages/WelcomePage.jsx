import React, { useContext } from "react";

import { Box, Typography } from "@mui/material";
import {
  AuthContext,
  ProfileComponent,
  WidePage,
  updateUserProfile,
} from "@micha.bigler/ui-core-micha";
import { useTranslation } from "react-i18next";
import { Helmet } from "react-helmet";
import { Navigate, useNavigate } from "react-router-dom";

const WelcomePage = () => {
  const { t } = useTranslation();
  const { login, user } = useContext(AuthContext);
  const navigate = useNavigate();

  if (user && !user.is_new) {
    return <Navigate to="/account" replace />;
  }

  const handleWelcomeSubmit = async (payload) => {
    const updatedUser = await updateUserProfile({
      ...payload,
      is_new: false,
    });
    login(updatedUser);

    if (payload.accepted_convenience_cookies) {
      document.cookie = "convenience_cookies=true;path=/;max-age=31536000";
    }

    navigate("/account");
  };

  return (
    <WidePage title={t("Welcome.PAGE_TITLE")}>
      <Helmet>
        <title>{t("Welcome.PAGE_TITLE")}</title>
      </Helmet>

      <Typography paragraph variant="h4">
        {t("Welcome.TITLE")}
      </Typography>

      <Typography paragraph>{t("Welcome.DESCRIPTION")}</Typography>

      <Box mt={2}>
        <ProfileComponent
          onSubmit={handleWelcomeSubmit}
          showCookies
          showName
          showPrivacy
          submitText={t("Welcome.CONTINUE")}
        />
      </Box>
    </WidePage>
  );
};

export default WelcomePage;
