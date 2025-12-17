/**
 * Enhanced Cloudflare Worker to handle deployment notifications and forward them to Slack
 * 
 * Features:
 * - Request authentication via Bearer token
 * - Input validation
 * - Structured error logging
 * - Configurable channel via environment variable
 * - Retry logic for Slack API calls
 * 
 * Environment variables required:
 * - SLACK_WEBHOOK_URL: Slack incoming webhook URL
 * - NOTIFICATION_TOKEN: Secret token for authenticating requests (optional but recommended)
 * - SLACK_CHANNEL: Slack channel name (optional, defaults to #web)
 */

export default {
  async fetch(request, env, ctx) {
    // Only accept POST requests
    if (request.method !== 'POST') {
      return new Response(
        JSON.stringify({ error: 'Method not allowed', allowed: ['POST'] }), 
        { 
          status: 405,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }

    // Authenticate request if token is configured
    if (env.NOTIFICATION_TOKEN) {
      const authHeader = request.headers.get('Authorization');
      const expectedAuth = `Bearer ${env.NOTIFICATION_TOKEN}`;
      
      if (!authHeader || authHeader !== expectedAuth) {
        console.error('Authentication failed', {
          hasAuth: !!authHeader,
          remoteIP: request.headers.get('CF-Connecting-IP')
        });
        
        return new Response(
          JSON.stringify({ error: 'Unauthorized' }), 
          { 
            status: 401,
            headers: { 'Content-Type': 'application/json' }
          }
        );
      }
    }

    try {
      // Parse and validate the incoming webhook payload
      let payload;
      try {
        payload = await request.json();
      } catch (e) {
        console.error('Invalid JSON payload', { error: e.message });
        return new Response(
          JSON.stringify({ error: 'Invalid JSON payload' }), 
          { 
            status: 400,
            headers: { 'Content-Type': 'application/json' }
          }
        );
      }
      
      // Validate required fields
      if (!payload || typeof payload !== 'object') {
        console.error('Payload is not an object', { payload });
        return new Response(
          JSON.stringify({ error: 'Payload must be an object' }), 
          { 
            status: 400,
            headers: { 'Content-Type': 'application/json' }
          }
        );
      }
      
      // Extract relevant information with defaults
      const {
        project_name = 'jkcoukblog',
        deployment_id = 'unknown',
        environment = 'production',
        url = 'https://jameskilby.co.uk',
        status,
        created_on,
        deployed_by = 'Cloudflare Pages',
        error_message
      } = payload;

      // Validate status field
      if (!status) {
        console.error('Missing required field: status', { payload });
        return new Response(
          JSON.stringify({ error: 'Missing required field: status' }), 
          { 
            status: 400,
            headers: { 'Content-Type': 'application/json' }
          }
        );
      }

      // Determine message color and emoji based on deployment status
      let color, emoji, statusText;
      switch (status) {
        case 'success':
          color = 'good';
          emoji = '🚀';
          statusText = 'deployed successfully';
          break;
        case 'failure':
          color = 'danger';
          emoji = '❌';
          statusText = 'deployment failed';
          break;
        case 'building':
          color = '#439FE0'; // Cloudflare blue
          emoji = '🔨';
          statusText = 'building';
          break;
        case 'queued':
          color = 'warning';
          emoji = '⏳';
          statusText = 'queued for deployment';
          break;
        default:
          color = 'warning';
          emoji = '🟡';
          statusText = `deployment ${status}`;
      }

      // Build Slack message fields
      const fields = [
        {
          title: 'Environment',
          value: environment,
          short: true
        },
        {
          title: 'Deployment ID',
          value: deployment_id,
          short: true
        },
        {
          title: 'Live URL',
          value: `<${url}|${url}>`,
          short: false
        }
      ];

      // Add staging URL for production deployments
      if (environment === 'production') {
        fields.push({
          title: 'Staging URL',
          value: '<https://jkcoukblog.pages.dev|jkcoukblog.pages.dev>',
          short: false
        });
      }

      // Add error message if deployment failed
      if (status === 'failure' && error_message) {
        fields.push({
          title: 'Error',
          value: error_message.substring(0, 300) + (error_message.length > 300 ? '...' : ''),
          short: false
        });
      }

      // Format the Slack message
      const slackMessage = {
        channel: env.SLACK_CHANNEL || '#web',
        username: 'Cloudflare Pages',
        icon_emoji: ':cloudflare:',
        attachments: [{
          color: color,
          title: `${emoji} ${project_name} ${statusText}`,
          fields: fields,
          footer: `Cloudflare Pages${deployed_by !== 'Cloudflare Pages' ? ` • Deployed by ${deployed_by}` : ''}`,
          ts: created_on ? Math.floor(new Date(created_on).getTime() / 1000) : Math.floor(Date.now() / 1000)
        }]
      };

      // Send to Slack with retry logic
      const maxRetries = 3;
      let lastError;
      
      for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
          const slackResponse = await fetch(env.SLACK_WEBHOOK_URL, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(slackMessage)
          });

          if (slackResponse.ok) {
            console.log('Notification sent successfully', {
              project: project_name,
              status,
              environment,
              attempt
            });
            
            return new Response(
              JSON.stringify({ 
                success: true, 
                message: 'Notification sent to Slack successfully' 
              }), 
              { 
                status: 200,
                headers: { 'Content-Type': 'application/json' }
              }
            );
          }

          const errorText = await slackResponse.text();
          lastError = errorText;
          
          console.error('Slack API error', {
            attempt,
            status: slackResponse.status,
            error: errorText
          });

          // Don't retry on 4xx errors (client errors)
          if (slackResponse.status >= 400 && slackResponse.status < 500) {
            break;
          }

          // Wait before retrying (exponential backoff)
          if (attempt < maxRetries) {
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
          }

        } catch (error) {
          lastError = error.message;
          console.error('Slack request failed', {
            attempt,
            error: error.message
          });

          if (attempt < maxRetries) {
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
          }
        }
      }

      // All retries failed
      return new Response(
        JSON.stringify({ 
          error: 'Failed to send Slack notification after retries',
          details: lastError 
        }), 
        { 
          status: 500,
          headers: { 'Content-Type': 'application/json' }
        }
      );

    } catch (error) {
      console.error('Unexpected error processing webhook', {
        error: error.message,
        stack: error.stack
      });
      
      return new Response(
        JSON.stringify({ 
          error: 'Internal server error',
          message: error.message 
        }), 
        { 
          status: 500,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }
  }
};
