/**
 * Cloudflare Worker to handle deployment notifications and forward them to Slack
 * Deploy this worker and use its URL as the webhook endpoint in Cloudflare Pages notifications
 */

export default {
  async fetch(request, env, ctx) {
    // Only accept POST requests
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    try {
      // Parse the incoming webhook payload from Cloudflare Pages
      const payload = await request.json();
      
      // Extract relevant information
      const {
        project_name = 'jkcoukblog',
        deployment_id,
        environment,
        url,
        status,
        created_on,
        deployed_by
      } = payload;

      // Determine message color and emoji based on deployment status
      let color, emoji, statusText;
      if (status === 'success') {
        color = 'good';
        emoji = '🚀';
        statusText = 'deployed successfully';
      } else if (status === 'failure') {
        color = 'danger';
        emoji = '❌';
        statusText = 'deployment failed';
      } else {
        color = 'warning';
        emoji = '🟡';
        statusText = `deployment ${status}`;
      }

      // Format the Slack message
      const slackMessage = {
        channel: '#web',
        username: 'Cloudflare Pages',
        icon_emoji: ':cloudflare:',
        attachments: [{
          color: color,
          title: `${emoji} ${project_name} ${statusText}`,
          fields: [
            {
              title: 'Environment',
              value: environment || 'production',
              short: true
            },
            {
              title: 'Deployment ID',
              value: deployment_id || 'unknown',
              short: true
            },
            {
              title: 'Live URL',
              value: url ? `<${url}|${url}>` : 'https://jameskilby.co.uk',
              short: false
            },
            {
              title: 'Staging URL',
              value: '<https://jkcoukblog.pages.dev|jkcoukblog.pages.dev>',
              short: false
            }
          ],
          footer: 'Cloudflare Pages',
          ts: created_on ? Math.floor(new Date(created_on).getTime() / 1000) : Math.floor(Date.now() / 1000)
        }]
      };

      // Send to Slack
      const slackResponse = await fetch(env.SLACK_WEBHOOK_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(slackMessage)
      });

      if (slackResponse.ok) {
        return new Response('Notification sent to Slack successfully', { status: 200 });
      } else {
        console.error('Slack API error:', await slackResponse.text());
        return new Response('Failed to send Slack notification', { status: 500 });
      }

    } catch (error) {
      console.error('Error processing webhook:', error);
      return new Response('Internal server error', { status: 500 });
    }
  }
};