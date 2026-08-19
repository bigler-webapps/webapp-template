import { describe, expect, it } from "vitest";

import i18n from "./index";

const RAW_KEY_PATTERN = /^[A-Za-z]+\.[A-Z0-9_]+$/;

describe("webapp-template i18n registration", () => {
  it("registers no value shaped like a raw i18n key", () => {
    const offenders = [];
    for (const [language, bundle] of Object.entries(i18n.options.resources)) {
      for (const [key, value] of Object.entries(bundle.translation)) {
        if (typeof value === "string" && RAW_KEY_PATTERN.test(value)) {
          offenders.push(`${language}:${key} -> ${value}`);
        }
      }
    }
    expect(offenders).toEqual([]);
  });

  it("resolves a kit-shipped SectionNav string in de, en and fr", () => {
    for (const language of ["de", "en", "fr"]) {
      const value = i18n.getResource(language, "translation", "SectionNav.TRIGGER_EYEBROW");
      expect(typeof value).toBe("string");
      expect(value.length).toBeGreaterThan(0);
      expect(RAW_KEY_PATTERN.test(value)).toBe(false);
    }
  });
});
