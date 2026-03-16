import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import { authTranslations } from "@micha.bigler/ui-core-micha";

import translations from "./translations.json";

const LANGUAGE_STORAGE_KEY = "project-template.language";

const mergedTranslations = {
  ...translations,
  ...authTranslations,
};

const resources = {
  de: { translation: {} },
  en: { translation: {} },
  fr: { translation: {} },
};

Object.entries(mergedTranslations).forEach(([key, value]) => {
  if (!value) {
    return;
  }

  Object.entries(value).forEach(([language, text]) => {
    if (resources[language]) {
      resources[language].translation[key] = text;
    }
  });
});

i18n.use(initReactI18next).init({
  resources,
  lng: (() => {
    try {
      return localStorage.getItem(LANGUAGE_STORAGE_KEY) || "de";
    } catch {
      return "de";
    }
  })(),
  supportedLngs: ["de", "en", "fr"],
  load: "languageOnly",
  fallbackLng: "de",
  interpolation: {
    escapeValue: false,
  },
  keySeparator: false,
  nsSeparator: false,
});

if (!i18n.__project_template_language_listener_attached__) {
  i18n.__project_template_language_listener_attached__ = true;
  i18n.on("languageChanged", (language) => {
    try {
      if (typeof language === "string" && language.length > 0) {
        localStorage.setItem(LANGUAGE_STORAGE_KEY, language);
      }
    } catch {
      // Ignore storage errors in private browsing environments.
    }
  });
}

export default i18n;
