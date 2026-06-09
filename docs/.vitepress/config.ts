/// <reference path="./env.d.ts" />

import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(defineConfig({
  base: process.env.VITEPRESS_BASE || '/',
  title: 'Velaris',
  description: 'Capability-driven testing framework',
  lang: 'en-US',
  lastUpdated: true,
  cleanUrls: true,
  ignoreDeadLinks: true,

  head: [
    ['meta', { name: 'theme-color', content: '#3dd68c' }],
    ['link', { rel: 'icon', type: 'image/png', href: '/brand/logo.png' }],
    ['link', { rel: 'apple-touch-icon', href: '/brand/logo.png' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' }],
    [
      'link',
      {
        rel: 'stylesheet',
        href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap',
      },
    ],
  ],

  markdown: {
    mermaid: true,
    lineNumbers: true,
  },

  themeConfig: {
    logo: '/brand/logo.png',
    siteTitle: 'Velaris',

    nav: [
      { text: 'Getting Started', link: '/getting-started/', activeMatch: '/getting-started/' },
      { text: 'How It\'s Different', link: '/concepts/how-velaris-is-different' },
      { text: 'Concepts', link: '/concepts/', activeMatch: '/concepts/' },
      { text: 'Architecture', link: '/architecture/', activeMatch: '/architecture/' },
      { text: 'Guide', link: '/guide/plugin-author', activeMatch: '/guide/' },
      { text: 'Examples', link: '/examples/', activeMatch: '/examples/' },
      {
        text: 'v0.1.0-alpha',
        items: [
          { text: 'Changelog', link: '/alpha-scope' },
          { text: 'Alpha scope', link: '/alpha-scope' },
        ],
      },
    ],

    sidebar: {
      '/getting-started/': [
        {
          text: 'Getting Started',
          items: [
            { text: 'Introduction', link: '/getting-started/' },
            { text: 'Installation', link: '/getting-started/installation' },
            { text: 'Your First Test', link: '/getting-started/first-test' },
            { text: 'Configuration', link: '/getting-started/configuration' },
            { text: 'CLI Reference', link: '/getting-started/cli' },
            { text: 'HTML Report', link: '/html-report' },
          ],
        },
      ],

      '/concepts/how-velaris-is-different': [
        {
          text: 'Concepts',
          items: [
            { text: 'How Velaris Is Different', link: '/concepts/how-velaris-is-different' },
            { text: 'Overview', link: '/concepts/' },
            { text: 'Capabilities', link: '/concepts/capabilities' },
            { text: 'Providers', link: '/concepts/providers' },
            { text: 'TestSpec IR', link: '/concepts/testspec' },
            { text: 'Events & Reporting', link: '/concepts/events' },
          ],
        },
      ],

      '/concepts/': [
        {
          text: 'Concepts',
          items: [
            { text: 'Overview', link: '/concepts/' },
            { text: 'How Velaris Is Different', link: '/concepts/how-velaris-is-different' },
            { text: 'Capabilities', link: '/concepts/capabilities' },
            { text: 'Providers', link: '/concepts/providers' },
            { text: 'TestSpec IR', link: '/concepts/testspec' },
            { text: 'Events & Reporting', link: '/concepts/events' },
          ],
        },
      ],

      '/architecture/': [
        {
          text: 'Architecture',
          items: [
            { text: 'Overview', link: '/architecture/' },
            { text: 'Execution Pipeline', link: '/architecture/execution-pipeline' },
            { text: 'Packages', link: '/architecture/packages' },
            { text: 'Model A Composition', link: '/architecture/model-a' },
            { text: 'Authoring Adapters', link: '/authoring-styles' },
          ],
        },
      ],

      '/guide/': [
        {
          text: 'Guides',
          items: [
            { text: 'Plugin Author Guide', link: '/guide/plugin-author' },
          ],
        },
        {
          text: 'Built-in Capabilities',
          items: [
            { text: 'Overview', link: '/guide/capabilities/' },
            { text: 'api@0.1', link: '/guide/capabilities/api' },
            { text: 'secrets@0.1', link: '/guide/capabilities/secrets' },
            { text: 'browser@0.1', link: '/guide/capabilities/browser' },
            { text: 'target_environment@0.1', link: '/guide/capabilities/target-environment' },
          ],
        },
      ],

      '/examples/': [
        {
          text: 'Examples',
          items: [
            { text: 'Overview', link: '/examples/' },
            { text: 'Browser', link: '/examples/browser' },
            { text: 'Authoring (Python/YAML/BDD)', link: '/examples/authoring' },
            { text: 'Reporting & HTML', link: '/examples/reporting' },
            { text: 'Plugins (clock)', link: '/examples/plugins' },
            { text: 'Stress Test', link: '/examples/stress-test' },
            { text: 'Composition', link: '/examples/composition' },
            { text: 'HTTP & Secrets', link: '/examples/minimal' },
          ],
        },
      ],
    },

    socialLinks: [],

    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2026 Velaris Contributors',
    },

    search: {
      provider: 'local',
    },

  },

  mermaid: {
    securityLevel: 'loose',
    fontFamily: 'JetBrains Mono, ui-monospace, monospace',
  },

  mermaidPlugin: {
    class: 'nx-mermaid',
  },
}))
