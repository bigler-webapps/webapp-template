const globals = require("globals");
const react = require("eslint-plugin-react");
const reactHooks = require("eslint-plugin-react-hooks");

module.exports = [
  {
    ignores: ["build/**", "dist/**", "node_modules/**", "coverage/**"],
  },
  {
    // Vitest test files
    files: ["src/**/*.{test,spec}.{js,jsx}"],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
        ...globals.es2021,
        ...globals.vitest,
      },
    },
  },
  {
    files: ["src/**/*.{js,jsx}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
      globals: {
        ...globals.browser,
        ...globals.node,
        ...globals.es2021,
      },
    },
    plugins: {
      react,
      "react-hooks": reactHooks,
    },
    rules: {
      eqeqeq: ["warn", "always", { null: "ignore" }],
      "no-empty": "warn",
      "no-dupe-keys": "error",
      "no-redeclare": "error",
      "no-undef": "error",
      "no-unreachable": "warn",
      "no-unsafe-finally": "warn",
      "no-unused-vars": "warn",
      "react/jsx-uses-vars": "warn",
      "react-hooks/rules-of-hooks": "warn",
      "react-hooks/exhaustive-deps": "warn",
    },
  },
];
