/// <reference path="./env.d.ts" />

import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

const base = process.env.VITEPRESS_BASE || '/'

/** Prefix a public asset path with the VitePress base (required for GitHub Pages). */
function withBase(path: string): string {
  const asset = path.replace(/^\//, '')
  return `${base}${asset}`
}

const gettingStartedSidebar = [
  {
    text: 'Getting Started',
    items: [
      { text: 'Introduction', link: '/getting-started/' },
      { text: 'Quickstart', link: '/getting-started/quickstart' },
      { text: 'Installation', link: '/getting-started/installation' },
      { text: 'Your First Test', link: '/getting-started/first-test' },
      { text: 'What Velaris Can Do Today', link: '/what-velaris-can-do-today' },
      { text: 'Configuration', link: '/getting-started/configuration' },
      { text: 'CLI Reference', link: '/getting-started/cli' },
    ],
  },
]

const advancedSidebar = [
  {
    text: 'Design & Architecture',
    items: [
      { text: 'Overview', link: '/architecture/' },
      { text: 'Execution Pipeline', link: '/architecture/execution-pipeline' },
      { text: 'Packages', link: '/architecture/packages' },
      { text: 'Model A Composition', link: '/architecture/model-a' },
    ],
  },
  {
    text: 'Authoring Internals',
    items: [
      { text: 'Authoring Adapters', link: '/authoring-styles' },
      { text: 'Executable YAML', link: '/executable-yaml' },
      { text: 'BDD Adapter', link: '/bdd-adapter' },
    ],
  },
  {
    text: 'Milestone Reports',
    items: [
      { text: 'HTML Report', link: '/html-report' },
      { text: 'CLI UX Redesign', link: '/cli-ux-redesign' },
      { text: 'Architecture Stability', link: '/architecture-stability-report' },
      { text: 'Alpha Readiness', link: '/alpha-readiness-report' },
      { text: 'Roadmap', link: '/roadmap' },
    ],
  },
  {
    text: 'RFCs',
    items: [
      { text: 'RFC-001 Capability Model', link: '/rfc/RFC-001-capability-model' },
      { text: 'RFC-002 TestSpec IR', link: '/rfc/RFC-002-testspec-ir' },
    ],
  },
]

const advancedMatch =
  '^/(architecture|authoring-styles|executable-yaml|bdd-adapter|html-report|cli-ux-redesign|architecture-stability-report|alpha-readiness-report|roadmap|rfc)'

export default withMermaid(defineConfig({
  base,
  title: 'Velaris',
  description: 'Capability-driven testing framework',
  lang: 'en-US',
  lastUpdated: true,
  cleanUrls: true,
  ignoreDeadLinks: true,

  head: [
    ['meta', { name: 'theme-color', content: '#3dd68c' }],
    ['link', { rel: 'icon', type: 'image/png', href: withBase('brand/logo.png') }],
    ['link', { rel: 'apple-touch-icon', href: withBase('brand/logo.png') }],
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
      { text: 'Getting Started', link: '/getting-started/quickstart', activeMatch: '/getting-started/' },
      { text: 'What Can It Do', link: '/what-velaris-can-do-today' },
      { text: 'Concepts', link: '/concepts/', activeMatch: '/concepts/' },
      { text: 'Examples', link: '/examples/', activeMatch: '/examples/' },
      { text: 'Guide', link: '/guide/capabilities/', activeMatch: '/guide/' },
      { text: 'Advanced', link: '/architecture/', activeMatch: advancedMatch },
      {
        text: 'v0.1.0-alpha',
        items: [
          { text: 'Changelog', link: '/alpha-scope' },
          { text: 'Alpha scope', link: '/alpha-scope' },
        ],
      },
    ],

    sidebar: {
      '/getting-started/': gettingStartedSidebar,
      '/what-velaris-can-do-today': gettingStartedSidebar,

      '/concepts/': [
        {
          text: 'Concepts',
          items: [
            { text: 'Overview', link: '/concepts/' },
            { text: 'Why Not pytest?', link: '/concepts/why-not-pytest' },
            { text: 'How Velaris Is Different', link: '/concepts/how-velaris-is-different' },
            { text: 'Capabilities', link: '/concepts/capabilities' },
            { text: 'Providers', link: '/concepts/providers' },
            { text: 'TestSpec IR', link: '/concepts/testspec' },
            { text: 'Events & Reporting', link: '/concepts/events' },
          ],
        },
      ],

      '/guide/': [
        {
          text: 'Introspection & Diagnostics',
          items: [
            { text: 'Test Discovery (collect)', link: '/guide/test-discovery' },
            { text: 'Capability Introspection', link: '/guide/capability-introspection' },
            { text: 'Environment Diagnostics (doctor)', link: '/guide/doctor' },
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
        {
          text: 'Plugin Development',
          items: [
            { text: 'Plugin Author Guide', link: '/guide/plugin-author' },
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

      // Advanced: architecture, internals, milestone reports, and RFCs.
      // Shared across all advanced pages so the sidebar stays consistent.
      '/architecture/': advancedSidebar,
      '/authoring-styles': advancedSidebar,
      '/executable-yaml': advancedSidebar,
      '/bdd-adapter': advancedSidebar,
      '/html-report': advancedSidebar,
      '/cli-ux-redesign': advancedSidebar,
      '/architecture-stability-report': advancedSidebar,
      '/alpha-readiness-report': advancedSidebar,
      '/roadmap': advancedSidebar,
      '/rfc/': advancedSidebar,
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
