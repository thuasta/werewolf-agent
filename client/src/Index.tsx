/*
    Entry point (client mount)

    说明：
    - 这个文件是 React 应用的入口，用来将 `App` 组件挂载到 `index.html` 中的 `#root` 容器。
    - `index.html`（项目根）通过 `<script type="module" src="/src/Index.tsx"></script>` 引入本模块。
    - 保持此文件尽量简单：只做挂载与严格模式包装，所有页面与路由由 `App` 管理。

    与比赛项目关联：前端负责可视化和交互（观战、回放、人工挑战），后端（或模拟引擎）负责游戏状态流。
*/

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Find the container element that will host the React tree.
// This ID must match the `<div id="root"></div>` in `index.html`.
const rootElement = document.getElementById('root');
if (!rootElement) {
    // Fail early if the HTML template doesn't provide the expected mount point.
    throw new Error("Could not find root element to mount to");
}

// Create React 18 root and render the top-level App component.
// Wrapping in StrictMode activates additional runtime checks in development.
const root = ReactDOM.createRoot(rootElement);
root.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);