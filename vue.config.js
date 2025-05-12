const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true
      }
    }
  },
  chainWebpack: config => {
    config.module
      .rule('js')
      .include
      .add(/node_modules\/@tdesign-vue-next\/chat/)
      .add(/node_modules\/marked/)
      .end()
      .use('babel-loader')
      .loader('babel-loader')
      .tap(options => {
        return {
          ...options,
          plugins: [
            ...(options.plugins || []),
            '@babel/plugin-transform-private-methods',
            '@babel/plugin-transform-private-property-in-object',
            '@babel/plugin-transform-class-properties',
            '@babel/plugin-proposal-class-properties'
          ]
        }
      });
  }
})
