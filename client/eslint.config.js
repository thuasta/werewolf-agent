import importPlugin from 'eslint-plugin-import';
import prettier from 'eslint-config-prettier';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import tseslint from 'typescript-eslint';
import unusedImports from 'eslint-plugin-unused-imports';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const tsconfigRootDir = path.dirname(fileURLToPath(import.meta.url));

/** @type {import('eslint').Linter.Config[]} */
export default [
    {
        ignores: ['dist/**', 'node_modules/**', 'coverage/**'],
        linterOptions: {
            reportUnusedDisableDirectives: true,
        },
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
            'unused-imports': unusedImports,
        },
        settings: {
            'import/resolver': {
                typescript: true,
            },
        },
        rules: {
            // 所有 import 语句出现在其他语句之前
            'import/first': 'error',
            // 禁止导入重复模块
            'import/no-duplicates': 'error',
            // 关闭无法解析模块的检查，由 TS 编译器处理
            'import/no-unresolved': 'off',
            // import 顺序和分组
            'import/order': [
                'error',
                {
                    'newlines-between': 'always',
                    alphabetize: { order: 'asc', caseInsensitive: true },
                    groups: [
                        ['builtin', 'external'],
                        'internal',
                        ['parent', 'sibling', 'index'],
                        'type',
                    ],
                },
            ],

            // 未使用的变量和导入
            'no-unused-vars': 'off',
            'unused-imports/no-unused-imports': 'error',
            'unused-imports/no-unused-vars': [
                'warn',
                {
                    vars: 'all',
                    varsIgnorePattern: '^_',
                    args: 'after-used',
                    argsIgnorePattern: '^_',
                },
            ],
        },
    },

    // TypeScript
    ...tseslint.configs.recommendedTypeChecked,
    {
        files: ['**/*.{ts,tsx}'],
        languageOptions: {
            parser: tseslint.parser,
            parserOptions: {
                project: ['./tsconfig.json'],
                tsconfigRootDir,
                ecmaFeatures: { jsx: true },
            },
        },
        rules: {
            '@typescript-eslint/consistent-type-imports': [
                'error',
                { prefer: 'type-imports', fixStyle: 'inline-type-imports' },
            ],
            '@typescript-eslint/no-floating-promises': 'error',
            '@typescript-eslint/no-misused-promises': [
                'error',
                {
                    checksVoidReturn: {
                        attributes: false,
                    },
                },
            ],
            '@typescript-eslint/no-unused-vars': 'off',
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
            ...reactRefresh.configs.vite.rules,

            // React 17+ JSX transform
            'react/react-in-jsx-scope': 'off',
            // TS 不需要 prop-types
            'react/prop-types': 'off',
        },
    },

    prettier,
];
