import React, { useContext } from "react";

import { Alert, Button, Stack, Typography } from "@mui/material";
import { AuthContext, WidePage } from "@micha.bigler/ui-core-micha";
import { useTranslation } from "react-i18next";
import { Helmet } from "react-helmet";
import { Link as RouterLink } from "react-router-dom";

const Home = () => {
  const { t } = useTranslation();
  const { user } = useContext(AuthContext);

  return (
    <WidePage title={t("App.NAME")}>
      <Helmet>
        <title>{t("Home.PAGE_TITLE")}</title>
      </Helmet>

      <Stack spacing={2.5}>
        <Typography variant="h4">{t("Home.TITLE")}</Typography>
        <Typography>{t("Home.DESCRIPTION")}</Typography>

        {user ? (
          <>
            <Alert severity="success">{t("Home.LOGGED_IN")}</Alert>
            {user.is_new && <Alert severity="info">{t("Home.NEW_USER_HINT")}</Alert>}
            <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5}>
              <Button component={RouterLink} to="/account" variant="contained">
                {t("Home.ACCOUNT_CTA")}
              </Button>
              {user.is_new && (
                <Button component={RouterLink} to="/welcome" variant="outlined">
                  {t("Home.WELCOME_CTA")}
                </Button>
              )}
            </Stack>
          </>
        ) : (
          <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5}>
            <Button component={RouterLink} to="/login" variant="contained">
              {t("Home.LOGIN_CTA")}
            </Button>
            <Button component={RouterLink} to="/signup" variant="outlined">
              {t("Home.SIGNUP_CTA")}
            </Button>
          </Stack>
        )}
      </Stack>
    </WidePage>
  );
};

export default Home;
