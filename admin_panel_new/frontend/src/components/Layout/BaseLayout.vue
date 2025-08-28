<template>
  <div class="layout-container">
    <!-- Header -->
    <Header />
    
    <!-- Main Content -->
    <main class="main-content">
      <slot />
    </main>
  </div>
</template>

<script>
import Header from './Header.vue'

export default {
  name: 'BaseLayout',
  components: {
    Header
  }
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.main-content {
  width: 100%;
  margin: 0 auto;
  padding: 30px 20px;
}
</style>
