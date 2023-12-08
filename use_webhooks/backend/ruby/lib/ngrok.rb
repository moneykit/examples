require 'faraday'

class NgrokError < StandardError
end


def get_ngrok_tunnel_to_backend
  # ngrok domain is the name of the service defined in docker-compose.yml
  conn = Faraday.new do |f|
    f.request :json
    f.response :json
  end

  begin
      response = conn.get("http://ngrok:4040/api/tunnels")
      raise NgrokError, "Failed to fetch ngrok tunnel's public url" if response.status != 200

      tunnels = response.body["tunnels"]
      for tunnel in tunnels do
          # find the one tunneling to backend_ruby:8000
          if tunnel["config"]["addr"] == "http://backend_ruby:8000"
              return tunnel["public_url"]
          end
      end
      raise NgrokError, "No tunnel for http://backend_ruby:8000 found"
  rescue Faraday::Error => e
      raise NgrokError, "Failed to fetch ngrok tunnel's public url"
  end
end
