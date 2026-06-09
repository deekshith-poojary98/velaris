<script setup lang="ts">
import DefaultTheme from 'vitepress/theme'

const { Layout } = DefaultTheme

const pipeline = [
  { t: 'Collect', d: 'Discover @test functions' },
  { t: 'TestSpec', d: 'Validate into IR' },
  { t: 'Resolve', d: 'Registry + config' },
  { t: 'Inject', d: 'Capabilities as params' },
  { t: 'Execute', d: 'Run the test' },
  { t: 'Events', d: 'Emit observations' },
  { t: 'Report', d: 'stdout + JSON log' },
]

const models = [
  { fw: 'pytest', unit: 'Fixtures', q: '“How do I build this?”' },
  { fw: 'Robot', unit: 'Keywords', q: '“What step is next?”' },
  { fw: 'Velaris', unit: 'Capabilities', q: '“What am I allowed to use?”', velaris: true },
]
</script>

<template>
  <Layout>
    <!-- Terminal showcase next to the hero copy -->
    <template #home-hero-image>
      <div class="nx-terminal">
        <div class="bar">
          <span class="dot r" />
          <span class="dot y" />
          <span class="dot g" />
          <span class="file">velaris run</span>
        </div>
        <div class="body">
          <div class="cmd"><span class="prompt">$</span> velaris run tests/</div>
          <div class="ok">✓ test_login</div>
          <div class="ok">✓ test_login_yaml</div>
          <div class="ok">✓ User logs in</div>
          <div class="spacer">&nbsp;</div>
          <div><span class="ok">Passed: 3</span>&nbsp;&nbsp;<span class="muted">Failed: 0</span></div>
          <div class="muted">Duration: 0.01s</div>
          <div class="spacer">&nbsp;</div>
          <div class="run">› --verbose for RUN/RESOLVE · --debug for capability trace</div>
          <div class="cmd"><span class="prompt">$</span> <span class="cursor" /></div>
        </div>
      </div>
    </template>

    <!-- Sections after the feature grid -->
    <template #home-features-after>
      <section class="nx-section nx-band">
        <div class="nx-eyebrow">One pipeline</div>
        <h2>Collect → TestSpec → Resolve → Inject → Execute → Events → Report</h2>
        <p class="lead">
          Every <code>velaris run</code> follows the same path. The runner operates on
          TestSpec — never on Python-specific types — so authoring stays decoupled from execution.
        </p>
        <div class="nx-pipeline">
          <div class="nx-step" v-for="(s, i) in pipeline" :key="s.t">
            <div class="n">{{ String(i + 1).padStart(2, '0') }}</div>
            <div class="t">{{ s.t }}</div>
            <div class="d">{{ s.d }}</div>
          </div>
        </div>
      </section>

      <section class="nx-section nx-band">
        <div class="nx-eyebrow">Mental model</div>
        <h2>A different unit of reuse</h2>
        <p class="lead">
          pytest centers on fixtures, Robot on keywords. Velaris centers on capabilities —
          named interfaces a test declares, with config choosing the implementation.
        </p>
        <div class="nx-models">
          <div
            class="nx-model"
            :class="{ 'is-velaris': m.velaris }"
            v-for="m in models"
            :key="m.fw"
          >
            <div class="fw">{{ m.fw }}</div>
            <div class="unit">{{ m.unit }}</div>
            <div class="q">{{ m.q }}</div>
          </div>
        </div>
      </section>
    </template>
  </Layout>
</template>
