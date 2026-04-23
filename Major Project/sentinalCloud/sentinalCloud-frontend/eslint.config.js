import globals from "globals";
import pluginJs from "@eslint/js";
import pluginReactConfig from "eslint-plugin-react/configs/recommended.js";
import pluginReactHooks from "eslint-plugin-react-hooks";
import pluginReactRefresh from "eslint-plugin-react-refresh";

export default [
  // Global configuration applies to all files
  {
    languageOptions: {
      globals: { ...globals.browser, ...globals.node }
    },
    // Ignore build output directory
    ignores: ["dist/**"],
  },

  // Base JavaScript rules
  pluginJs.configs.recommended,

  // React-specific rules and settings
  {
    files: ["**/*.{js,jsx}"],
    ...pluginReactConfig, // Spread the recommended React config
    settings: {
      react: {
        // Automatically detect the version of React to use
        version: "detect",
      },
    },
    plugins: {
      "react-hooks": pluginReactHooks,
      "react-refresh": pluginReactRefresh,
    },
    rules: {
      // Apply recommended rules for React Hooks
      ...pluginReactHooks.configs.recommended.rules,
      
      // Enforce that only components are exported from files used by React Refresh
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],

      // Rule adjustments for modern React with Vite
      "react/react-in-jsx-scope": "off", // Not needed with the new JSX transform
      "react/prop-types": "off", // Disable if you are not using PropTypes
      "no-unused-vars": ["warn", { "argsIgnorePattern": "^_" }], // Warn about unused variables
    },
  },
];