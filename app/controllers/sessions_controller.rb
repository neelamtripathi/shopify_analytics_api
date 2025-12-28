class SessionsController < ApplicationController
  def new
    shop = params[:shop]

    redirect_to ShopifyAPI::Auth::AuthQuery.new(
      shop: shop,
      client_id: ENV["SHOPIFY_API_KEY"],
      scopes: ENV["SHOPIFY_SCOPES"],
      redirect_uri: "#{ENV['APP_URL']}/auth/shopify/callback"
    ).redirect_url
  end

  def callback
    result = ShopifyAPI::Auth::OAuth.validate_auth_callback(
      cookies: cookies,
      query: request.query_parameters,
      shop: request.query_parameters["shop"]
    )

    session[:shop] = result.shop
    session[:access_token] = result.access_token

    redirect_to root_path
  end
end
