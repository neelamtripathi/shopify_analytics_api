class ShopifyController < ApplicationController
  def auth
    shop = params[:shop]

    if shop.blank?
      render plain: "Missing shop parameter", status: 400
      return
    end

    redirect_to(
      "https://#{shop}/admin/oauth/authorize" \
      "?client_id=#{ENV['SHOPIFY_API_KEY']}" \
      "&scope=read_products,read_orders" \
      "&redirect_uri=#{ENV['SHOPIFY_REDIRECT_URI']}",
      allow_other_host: true
    )

  end

  def callback
    render plain: "Shopify OAuth callback successful ✅"
  end
end
