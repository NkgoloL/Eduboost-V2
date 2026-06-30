/*
 * FE-PR-003: establish explicit ESLint config so future lint hardening
 * can build on a checked-in baseline rather than the implicit Next.js defaults.
 */
module.exports = {
  root: true,
  extends: ["next/core-web-vitals"],
  env: {
    browser: true,
    es2021: true,
    jest: false,
    node: true,
  },
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
  },
  parser: "@typescript-eslint/parser",
  plugins: ["@typescript-eslint"],
  rules: {
    "@typescript-eslint/no-explicit-any": "warn",
    "no-console": ["error", { allow: ["warn", "error"] }],
    "no-restricted-syntax": [
      "error",
      {
        selector:
          "CallExpression[callee.object.name='console'][arguments.0.type='Identifier'][arguments.0.name=/email|phone|idNumber|learnerName|guardianName|consent|token|jwt|session|password/i]",
        message: "Do not log potential PII or secrets. Use monitoring scrubbing instead.",
      },
      {
        selector:
          "CallExpression[callee.object.name='console'][arguments.0.type='Literal'][arguments.0.value=/email|phone|idNumber|learnerName|guardianName|consent|token|jwt|session|password/i]",
        message: "Do not log potential PII or secrets. Use monitoring scrubbing instead.",
      },
    ],
  },
};
