import pandas as pd
import html
import re
from datetime import datetime

def get_date(business_key):

    data = pd.read_excel("form_data.xlsx")
    data = data.set_index("businessKey")

    return data.loc[business_key, "feedbackDate"]





# Marker regexes
RE_QUERY_HEAD = re.compile(r"\n{0,2}Unsere Rückfrage an Sie:\n", re.MULTILINE)
RE_RESPONSE_HEAD = re.compile(r"\n{0,2}Rückmeldung vom (\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}):\n", re.MULTILINE)

def split_conversation(full_text: str):

   initial_end = None
   conversations: list[tuple[str, str, str]] = []


   pos = 0
   first_query_match = RE_QUERY_HEAD.search(full_text)
   if first_query_match:
       initial_end = first_query_match.start()
   else:
       # No query marker at all
       return full_text.strip(), []


   initial = full_text[:initial_end].strip()


   while True:
       q_match = RE_QUERY_HEAD.search(full_text, pos)
       if not q_match:
           break
       q_start = q_match.end()
       r_match = RE_RESPONSE_HEAD.search(full_text, q_start)
       if not r_match:
           # No response for this query → unanswered → stop parsing pairs
           break
       # Extract query text (up to response marker)
       query_text = full_text[q_start : r_match.start()].strip()
       ts = r_match.group(1)
       # Find start of next query to slice the answer properly
       next_q_match = RE_QUERY_HEAD.search(full_text, r_match.end())
       if next_q_match:
           answer_text = full_text[r_match.end() : next_q_match.start()].strip()
           pos = next_q_match.start()
       else:
           answer_text = full_text[r_match.end() :].strip()
           pos = len(full_text)
       conversations.append((query_text, ts, answer_text))


   return initial, conversations





def newline_to_br(text: str):

    return html.escape(text).replace("\n", "<br>")





def space_to_nbsp(text: str):
    return html.escape(text).replace("\n", "<br>")





def get_simple_html_mail(message_header, message):

    year = datetime.now().year

    content_card = f"""
      <tr>
        <td style="background-color:#0073b3;padding:24px 32px;">
          <h1 style="margin:0;font-size:24px;color:#ffffff;font-weight:normal;">
            {space_to_nbsp(message_header)}
          </h1>
        </td>
      </tr>

      <tr>
        <td style="padding:32px;color:#333333;">
          <p>{newline_to_br(message)}</p>
        </td>
      </tr>
    """


    html_body = f"""
    <html>
      <body style="margin:0;padding:0;background-color:#f5f7fa;font-family:Arial,Helvetica,sans-serif;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f7fa;">
          <tr>
            <td align="center" style="padding:30px 10px;">
              <table role="presentation" width="600" cellpadding="0" cellspacing="0"
                     style="background-color:#ffffff;border-radius:8px;
                            box-shadow:0 2px 8px rgba(0,0,0,0.05);overflow:hidden;">
                            
                {content_card}

                <tr>
                  <td style="background-color:#f0f2f4;padding:16px;text-align:center;
                             font-size:12px;color:#666666;">
                    © {year}&nbsp;Digipro&nbsp;Demo&nbsp;AG&nbsp;• Alle&nbsp;Rechte&nbsp;vorbehalten
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    return html_body




def get_quote_html_mail(message_header, message_before_quote, quote, message_after_quote):
    year = datetime.now().year

    content_card = f"""
      <tr>
        <td style="background-color:#0073b3;padding:24px 32px;">
          <h1 style="margin:0;font-size:24px;color:#ffffff;font-weight:normal;">
            {space_to_nbsp(message_header)}
          </h1>
        </td>
      </tr>

      <tr>
        <td style="padding:32px;color:#333333;">
          <p>{newline_to_br(message_before_quote)}</p>
            <blockquote style="margin:0;border-left:4px solid #0073b3; padding:16px;background-color:#f0f8ff;">
                <em>{newline_to_br(quote)}</em>
            </blockquote>
          <p>{newline_to_br(message_after_quote)}</p>
        </td>
      </tr>
    """

    html_body = f"""
    <html>
      <body style="margin:0;padding:0;background-color:#f5f7fa;font-family:Arial,Helvetica,sans-serif;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f7fa;">
          <tr>
            <td align="center" style="padding:30px 10px;">
              <table role="presentation" width="600" cellpadding="0" cellspacing="0"
                     style="background-color:#ffffff;border-radius:8px;
                            box-shadow:0 2px 8px rgba(0,0,0,0.05);overflow:hidden;">

                {content_card}

                <tr>
                  <td style="background-color:#f0f2f4;padding:16px;text-align:center;
                             font-size:12px;color:#666666;">
                    © {year}&nbsp;Digipro&nbsp;Demo&nbsp;AG&nbsp;• Alle&nbsp;Rechte&nbsp;vorbehalten
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    return html_body




def get_conversation_html_mail(message_header, message_before_conv, conversation, message_after_conv, button_text, link):

    year = datetime.now().year

    initial, convs = split_conversation(conversation)

    conv_html = ""
    for query_text, ts, answer in convs:
        conv_html += f"""
            <h3 style="margin:24px 0 8px;color:#0073b3;font-weight:normal;">
              Unsere&nbsp;Rückfrage&nbsp;an&nbsp;Sie
            </h3>
            <blockquote style="margin:0 0 24px;border-left:4px solid #0073b3; padding:16px;background-color:#f0f8ff;">
              {newline_to_br(query_text)}
            </blockquote>
            <h3 style="margin:0 0 8px;color:#0073b3;font-weight:normal;">
              Rückmeldung&nbsp;vom&nbsp;{ts}
            </h3>
            <blockquote style="margin:0 0 24px;border-left:4px solid #0073b3;
                               padding:16px;background-color:#f0f8ff;">
              {newline_to_br(answer)}
            </blockquote>
        """


    content_card = f"""
      <tr>
        <td style="background-color:#0073b3;padding:24px 32px;">
          <h1 style="margin:0;font-size:24px;color:#ffffff;font-weight:normal;">
            {space_to_nbsp(message_header)}
          </h1>
        </td>
      </tr>

      <tr>
        <td style="padding:32px;color:#333333;">
          <p>{newline_to_br(message_before_conv)}</p>
            <blockquote style="margin:0;border-left:4px solid #0073b3; padding:16px;background-color:#f0f8ff;">
                <em>{newline_to_br(initial)}</em>
            </blockquote>
          
            {conv_html}
            
          <p>{newline_to_br(message_after_conv)}</p>
          <p style="text-align:center;margin:32px 0;">
            <a href="{link}" style="background-color:#0073b3;color:#ffffff;text-decoration:none;
            padding:12px 24px;border-radius:4px;font-weight:bold;display:inline-block;">{space_to_nbsp(button_text)}</a>
          </p>
        </td>
      </tr>
    """

    html_body = f"""
    <html>
      <body style="margin:0;padding:0;background-color:#f5f7fa;font-family:Arial,Helvetica,sans-serif;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f7fa;">
          <tr>
            <td align="center" style="padding:30px 10px;">
              <table role="presentation" width="600" cellpadding="0" cellspacing="0"
                     style="background-color:#ffffff;border-radius:8px;
                            box-shadow:0 2px 8px rgba(0,0,0,0.05);overflow:hidden;">

                {content_card}

                <tr>
                  <td style="background-color:#f0f2f4;padding:16px;text-align:center;
                             font-size:12px;color:#666666;">
                    © {year}&nbsp;Digipro&nbsp;Demo&nbsp;AG&nbsp;• Alle&nbsp;Rechte&nbsp;vorbehalten
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    return html_body



print(get_date(6237336537214213147))