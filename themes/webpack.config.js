var path = require('path');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
var BundleTracker = require('webpack-bundle-tracker');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const TerserPlugin = require("terser-webpack-plugin");
const CopyPlugin = require("copy-webpack-plugin");

module.exports = {
  target: ["web", 'es5'],
  context: __dirname,
  mode: 'development',
  entry: {
    main: {
      import: './source/main.js',
      dependOn: 'shared'
    },
    shared: [
      'bootstrap/dist/js/bootstrap.bundle.js',
      'regenerator-runtime/runtime.js',
      'alpinejs',
    ]
  },
  output: {
    path: path.resolve('../coreplus/static/coreplus/'),
    chunkFilename: 'js/[name].bundle.js',
    filename: "js/[name].js",
    clean: true,
  },
  optimization: {
    runtimeChunk: 'single',
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          format: {
            comments: false,
          },
        },
        extractComments: false,
      }),
      new CssMinimizerPlugin({
        minimizerOptions: {
          preset: [
            "default",
            {
              discardComments: { removeAll: true },
            },
          ],
        },
      })
    ],
  },
  devServer: {
    host: '127.0.0.1',
    port: 9000,
    hot: true,
    allowedHosts: "all",
    static: {
      watch: true,
    },
    devMiddleware: {
      writeToDisk: true,
    },
  },
  module: {
    rules: [{
      test: /\.css$/,
      use: ['style-loader', 'css-loader', 'postcss-loader']
    }, {
      test: /\.js$/,
      use: {
        loader: 'babel-loader',
        options: {
          presets: [
            [
              '@babel/preset-env',
              {
                targets: {
                  esmodules: true,
                },
              },
            ],
          ],
        },
      }
    }, {
      test: /\.s[ac]ss$/i,
      use: [
        // fallback to style-loader in development
        MiniCssExtractPlugin.loader,
        'css-loader',
        'sass-loader'
      ]
    }, {
      test: /\.(eot|woff|woff2|ttf)$/,
      type: 'asset/resource',
      generator: {
        filename: 'fonts/[name][ext]'
      }
    }, {
      test: /\.(svg|png|jpe?g|gif|ico)$/i,
      type: 'asset/resource',
      generator: {
        filename: 'img/[name][ext]',
      }
    }]
  },
  plugins: [
    new CleanWebpackPlugin({
      dry: true
    }),
    new CopyPlugin({
      patterns: [
        { from: "./source/img", to: "./img" },
        { from: "./source/css/plugins", to: "./css/plugins" },
        { from: "./source/plugins", to: "./js/plugins" },
      ],
    }),
    new BundleTracker({
      filename: './webpack-stats.json'
    }),
    new MiniCssExtractPlugin({
      filename: 'css/[name].bundle.css'
    }),
  ]
}
