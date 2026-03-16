import React, { useContext, useEffect } from "react";

import {
  AppBar,
  Box,
  Button,
  FormControl,
  MenuItem,
  Select,
  Toolbar,
  Typography,
} from "@mui/material";
import {
  AuthContext,
  updateUserProfile,
} from "@micha.bigler/ui-core-micha";
import { useTranslation } from "react-i18next";
import { Link as RouterLink, useNavigate } from "react-router-dom";

const LANGUAGE_OPTIONS = [
  { code: "de", label: "DE" },
  { code: "en", label: "EN" },
  { code: "fr", label: "FR" },
];

const Header = () => {
  const { i18n, t } = useTranslation();
  const { login, logout, user } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    if (user?.language && i18n.resolvedLanguage !== user.language) {
      i18n.changeLanguage(user.language);
    }
  }, [i18n, user?.language]);

  const handleLanguageChange = async (event) => {
    const nextLanguage = event.target.value;
    await i18n.changeLanguage(nextLanguage);

    if (!user) {
      return;
    }

    try {
      const updatedUser = await updateUserProfile({ language: nextLanguage });
      login(updatedUser);
    } catch {
      // Keep the local language change even if persisting it fails.
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <AppBar position="static">
      <Toolbar sx={{ gap: 1.5 }}>
        <Typography
          component={RouterLink}
          sx={{ color: "inherit", flexGrow: 1, textDecoration: "none" }}
          to="/"
          variant="h6"
        >
          {t("App.NAME")}
        </Typography>

        <Button color="inherit" component={RouterLink} to="/">
          {t("Header.HOME")}
        </Button>

        {user?.is_new && (
          <Button color="inherit" component={RouterLink} to="/welcome">
            {t("Header.WELCOME")}
          </Button>
        )}

        {user ? (
          <Button color="inherit" component={RouterLink} to="/account">
            {t("Header.ACCOUNT")}
          </Button>
        ) : (
          <Button color="inherit" component={RouterLink} to="/login">
            {t("Header.LOGIN")}
          </Button>
        )}

        <FormControl size="small" sx={{ minWidth: 84 }}>
          <Select
            aria-label={t("Header.LANGUAGE")}
            onChange={handleLanguageChange}
            sx={{
              color: "inherit",
              ".MuiOutlinedInput-notchedOutline": { borderColor: "rgba(255,255,255,0.35)" },
              ".MuiSvgIcon-root": { color: "inherit" },
            }}
            value={i18n.resolvedLanguage || "de"}
          >
            {LANGUAGE_OPTIONS.map((language) => (
              <MenuItem key={language.code} value={language.code}>
                {language.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {user && (
          <Button color="inherit" onClick={handleLogout}>
            {t("Header.LOGOUT")}
          </Button>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Header;
