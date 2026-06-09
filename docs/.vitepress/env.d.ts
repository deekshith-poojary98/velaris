/// <reference types="vitepress/client" />

import type {} from 'vitepress'

declare module 'vitepress' {
  interface MarkdownOptions {
    mermaid?: boolean
  }
}
