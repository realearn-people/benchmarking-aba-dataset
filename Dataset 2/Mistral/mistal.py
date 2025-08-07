import pandas as pd
import requests
import json
import re


# ---------- Load Dataset ----------
file_path = '/Users/nonny/Downloads/Remove Disagreement Version(2).xlsx'
df = pd.read_excel(file_path)
df = df.rename(columns={'Column1': 'ID'})

df_positive = df[['ID', 'PositiveReview']].rename(columns={'PositiveReview': 'Review'})
df_negative = df[['ID', 'NegativeReview']].rename(columns={'NegativeReview': 'Review'})

df_positive = df_positive[df_positive['Review'].notna() & (df_positive['Review'].str.strip() != "")]
df_negative = df_negative[df_negative['Review'].notna() & (df_negative['Review'].str.strip() != "")]

df_positive = df_positive.drop_duplicates()
df_negative = df_negative.drop_duplicates()

df_combined = pd.concat([df_positive, df_negative], ignore_index=True)
df_combined = df_combined.sort_values(by=['ID']).reset_index(drop=True)

df_combined.head(30)

# ---------- Build Prompt ----------
def build_full_prompt(messages):
    return "\n\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages])

# ---------- Parse JSON Response ----------
def parse_response(response_json, review_id, full_prompt):
    results = []
    try:
        response_json = response_json.strip()

        # Remove "Assistant:" prefix if exists
        if response_json.lower().startswith("assistant:"):
            response_json = response_json[len("Assistant:"):].strip()

        # Fix double closing braces
        if response_json.endswith('}}'):
            response_json = response_json[:-1]  # remove extra '}'

        parsed = json.loads(response_json)
        topics_list = parsed["Topics"]
        for topic_group in topics_list:
            for topic, entries in topic_group.items():
                for entry in entries:
                    text = entry.get("text") or ""
                    label = entry.get("label") or ""
                    results.append({
                        "ID": review_id,
                        "FullPrompt": full_prompt,
                        "Topics": topic,
                        "Text": text,
                        "NegPos": label
                    })
    except Exception as e:
        print(f" Failed to parse ID {review_id}: {e}")
        print(f"Raw Response:\n{response_json}\n")
    return results


# ---------- Send Prompt   ----------
def send_prompt(review_text):
    system_prompt = (
        'Please output the following [text] according to the [constraints] in the [output format].\n '
        '[constraints]* The output should only be in the [output format], and you must classify which part of the text corresponds to which Topic in the [Topics]. '
        'Additionally, determine whether each classified element is Positive or Negative. If there is no corresponding element, put Null for both `text` and `label`. '
        'The most important constraint is not to include any extra characters such as newline characters, `json`, or backticks, or any other unnecessary text outside of the [output format]. '
        'If there are two or more elements of the same Topic, number each so that they do not conflict when converted to json format data. '
        'However, if they have the same NegPos label, keep them in one Text as much as possible.* \n '
        '[Topics] Room, Staff, Location, Food, Price, Facility, Check-in, Check-out, Taxi-issue, Booking-issue, Off \n\n '
        '[output format] '
        '{"Topics":[{"Room":[{"text": "test","label": "Positive"}],'
        '"Staff":[{"text": null,"label": null}],'
        '"Location":[{"text": "test","label": "Positive"}],'
        '"Food":[{"text": "test","label": "Negative"}],'
        '"Price":[{"text": "test","label": "Positive"}],'
        '"Facility":[{"text": "test","label": "Negative"}],'
        '"Check-in":[{"text": "test","label": "Positive"}],'
        '"Check-out":[{"text": null,"label": null}],'
        '"Taxi-issue":[{"text": null,"label": null}],'
        '"Booking-issue":[{"text": null,"label": null}],'
        '"Off":[{"text": null,"label": null}]}]}'
    )

    messages = [
        {"role": "system", "content": system_prompt},

           # Example 1
        {"role": "user", "content": "The room is enough big. But the room was a little bit dirty."},
        {"role": "assistant", "content": '{"Topics":[{"Room1":[{"text": "The room is enough big.","label": "Positive"}],'
                                         '"Room2":[{"text": "the room was a little bit dirty.","label": "Negative"}],'
                                         '"Staff":[{"text": null,"label": null}],'
                                         '"Location":[{"text": null,"label": null}],'
                                         '"Food":[{"text": null,"label": null}],'
                                         '"Price":[{"text": null,"label": null}],'
                                         '"Facility":[{"text": null,"label": null}],'
                                         '"Check-in":[{"text": null,"label": null}],'
                                         '"Check-out":[{"text": null,"label": null}],'
                                         '"Taxi-issue":[{"text": null,"label": null}],'
                                         '"Booking-issue":[{"text": null,"label": null}],'
                                         '"Off":[{"text": null,"label": null}]}]}'},

        
        # Example 2
        {"role": "user", "content": "The room was very clean, well decorated and modern, although not big. It was cheap."},
        {"role": "assistant", "content": '{"Topics":[{"Room1":[{"text": "The room was very clean, well decorated and modern","label": "Positive"}],'
                                         '"Room2":[{"text": "although not big","label": "Negative"}],'
                                         '"Price":[{"text": "cheap","label": "Positive"}],'
                                         '"Staff":[{"text": null,"label": null}],'
                                         '"Location":[{"text": null,"label": null}],'
                                         '"Food":[{"text": null,"label": null}],'
                                         '"Facility":[{"text": null,"label": null}],'
                                         '"Check-in":[{"text": null,"label": null}],'
                                         '"Check-out":[{"text": null,"label": null}],'
                                         '"Taxi-issue":[{"text": null,"label": null}],'
                                         '"Booking-issue":[{"text": null,"label": null}],'
                                         '"Off":[{"text": null,"label": null}]}]}'},

         # Example 3
        {"role": "user", "content": "Location. The hotel was new and close to the airport, which made traveling easy. However, there was a lot of street noise outside the window. Staff. The receptionist was polite and friendly. However, check-in took longer than expected. The hotel lobby was welcoming and spacious. The room had a comfortable bed, but the air conditioning was loud at night. The neighbors were noisy through the walls, and the WiFi in the room was weak and unreliable. The breakfast buffet was delicious; however, the coffee was terrible. The price was reasonable for the quality. The building was charming with historical architecture."},
        {"role": "assistant", "content": '{"Topics":[{"Room1":[{"text": "The room had a comfortable bed.","label": "Positive"}],'
                               '"Room2":[{"text": "The air conditioning was loud at night.","label": "Negative"}],'
                               '"Room3":[{"text": "The neighbors were noisy through the walls.","label": "Negative"}],'
                               '"Room4":[{"text": "the WiFi in the room was weak and unreliable.","label": "Negative"}],'
                               '"Staff":[{"text": "The receptionist was polite and friendly.","label": "Positive"}],'
                               '"Location1":[{"text": "close to the airport, which made traveling easy.","label": "Positive"}],'
                               '"Location2":[{"text": "there was a lot of street noise outside the window.","label": "Negative"}],'
                               '"Food1":[{"text": "The breakfast buffet was delicious.","label": "Positive"}],'
                               '"Food2":[{"text": "the coffee was terrible.","label": "Negative"}],'
                               '"Price":[{"text": "The price was reasonable for the quality.","label": "Positive"}],'
                               '"Facility1":[{"text": "The hotel was new.","label": "Positive"}],'
                               '"Facility2":[{"text": "The hotel lobby was welcoming and spacious.","label": "Positive"}],'
                               '"Facility3":[{"text": "The building was charming with historical architecture.","label": "Positive"}],'
                               '"Check-in":[{"text": "check-in took longer than expected.","label": "Negative"}],'
                               '"Check-out":[{"text": null,"label": null}],'
                               '"Taxi-issue":[{"text": null,"label": null}],'
                               '"Booking-issue":[{"text": null,"label": null}],'
                               '"Off":[{"text": "Location. Staff.","label": null}]}]}'
        },

        # Example 4
        {"role": "user", "content": "location, service, overall was good, Sure worth it to come back again"},
        {"role": "assistant", "content": '{"Topics":[{"Room":[{"text": null,"label": null}],'
                                '"Staff":[{"text": null,"label": null}],'
                                '"Location":[{"text": null,"label": null}],'
                                '"Food":[{"text": null,"label": null}],'
                                '"Price":[{"text": null,"label": null}],'
                                '"Facility":[{"text": null,"label": null}],'
                                '"Check-in":[{"text": null,"label": null}],'
                                '"Check-out":[{"text": null,"label": null}],'
                                '"Taxi-issue":[{"text": null,"label": null}],'
                                '"Booking-issue":[{"text": null,"label": null}],'
                                '"Off":[{"text": "location, service, overall was good, Sure worth it to come back again","label": "Null"}]}]}'
        },

         # Example 5
        {"role": "user", "content": "The apartment was new. The breakfast was amazing and the price was quite reasonable. Overall, we definitely planning to return again soon!"},
        {"role": "assistant", "content": '{"Topics":[{"Room":[{"text": null,"label": null}],'
                                '"Staff":[{"text": null,"label": null}],'
                                '"Location":[{"text": null,"label": null}],'
                                '"Food":[{"text": "The breakfast was amazing and the price was quite reasonable.","label": "Positive"}],'
                                '"Price":[{"text": null,"label": null}],'
                                '"Facility":[{"text": "The apartment was new.","label": "Positive"}],'
                                '"Check-in":[{"text": null,"label": null}],'
                                '"Check-out":[{"text": null,"label": null}],'
                                '"Taxi-issue":[{"text": null,"label": null}],'
                                '"Booking-issue":[{"text": null,"label": null}],'
                                '"Off":[{"text": "Overall, we definitely planning to return again soon!","label": "Positive"}]}]}'
        },
        
        {"role": "user", "content": review_text}
    ]
    full_prompt = build_full_prompt(messages)

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral:7b",
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0,
                    "top_p": 0.05
                }
            }
        )
        result = response.json()
        return result["response"], full_prompt
    except Exception as e:
        print(f" Error sending prompt to Mistral: {e}")
        return "", full_prompt

# ---------- Run All Reviews 3 Times ----------
for run_num in range(2, 4):
    print(f"\n Starting Run {run_num}...\n")
    final_results = []

    for idx, row in df_combined.iterrows():
        review_text = row['Review']
        review_id = row['ID']

        print(f"[Run {run_num}] Processing ID {review_id}...")
        try:
            response_content, full_prompt = send_prompt(review_text)
            print(f"[Run {run_num}] Raw response for ID {review_id}:\n{response_content}\n")

            parsed = parse_response(response_content, review_id, full_prompt)
            final_results.extend(parsed)

        except Exception as e:
            print(f"[Run {run_num}] Error processing ID {review_id}: {e}")

    # Save each run separately
    df_output = pd.DataFrame(final_results)
    output_path = f"output_formatted_ABA_dataset_2_mistral_5_shot_{run_num}.csv"
    df_output.to_csv(output_path, index=False)
    print(f"Saved Run {run_num} to {output_path}")
