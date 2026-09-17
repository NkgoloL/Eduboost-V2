import nextCoreWebVitals from "eslint-config-next/core-web-vitals";

const eslintConfig = [
  ...nextCoreWebVitals,
  {
    files: ["**/*.ts", "**/*.tsx"],
    rules: {
      // React 18 compatibility: disable experimental React 19 compiler rules
      "react-hooks/set-state-in-effect": "off",
      "react-hooks/preserve-manual-memoization": "off",
      "react-hooks/immutability": "off",
      "react-hooks/purity": "off",

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
  },
];

export default eslintConfig;
