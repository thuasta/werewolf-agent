import importPlugin from 'eslint-plugin-import';
import prettier from 'eslint-config-prettier';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import tseslint from 'typescript-eslint';

/** @type {import('eslint').Linter.Config[]} */
export default [
    {
        ignores: ['dist/**', 'node_modules/**', 'coverage/**'],
    },
    {
        files: ['**/*.{js,jsx,ts,tsx}'],
        languageOptions: {
            ecmaVersion: 'latest',
            sourceType: 'module',
            globals: {
                // Browser
                window: 'readonly',
                document: 'readonly',
                navigator: 'readonly',
                location: 'readonly',

                // Web APIs
                fetch: 'readonly',
                Request: 'readonly',
                Response: 'readonly',
                Headers: 'readonly',
                URL: 'readonly',

                // Runtime
                console: 'readonly',
                setTimeout: 'readonly',
                clearTimeout: 'readonly',
                setInterval: 'readonly',
                clearInterval: 'readonly',
            },
        },
        plugins: {
            import: importPlugin,
        },
        settings: {
            'import/resolver': {
                typescript: true,
            },
        },
        rules: {
            // 所有 import 语句出现在其他语句之前
            'import/first': 'error',
            // 禁止导入重复的模块
            'import/no-duplicates': 'error',
            // 关闭无法解析模块的检查，由 TS 编译器处理
            'import/no-unresolved': 'off',
        },
    },

    // TypeScript
    ...tseslint.configs.recommended,

    {
        files: ['**/*.{ts,tsx}'],
        languageOptions: {
            parser: tseslint.parser,
            parserOptions: {
                ecmaFeatures: { jsx: true },
            },
        },
    },

    // React
    {
        files: ['**/*.{jsx,tsx}'],
        plugins: {
            react,
            'react-hooks': reactHooks,
            'react-refresh': reactRefresh,
        },
        settings: {
            react: { version: 'detect' },
        },
        rules: {
            ...react.configs.recommended.rules,
            ...reactHooks.configs.recommended.rules,

            // React 17+ JSX transform
            'react/react-in-jsx-scope': 'off',
            // TS 不需要 prop-types
            'react/prop-types': 'off',

            // Vite Fast Refresh
            'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
        },
    },

    prettier,
];
