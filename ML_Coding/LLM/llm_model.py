__author__ = "Vivek"
__author_email__ = "vivekltp120@gmail.com"

from torchtext.datasets import AG_NEWS
from transformers import AutoModelWithLMHead, AdamW
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("gpt2")

EPOCHS = 50


def preprocess_data(data_iter):
    data = [tokenizer.encode(text) for _, text in data_iter]
    return data


train_iter = AG_NEWS(split='train')
train_data = preprocess_data(train_iter)


model = AutoModelWithLMHead.from_pretrained("gpt2")
optimizer = AdamW(model.parameters())

model.train()
for epoch in range(EPOCHS):
    for batch in train_data:
        outputs = model(batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()


prompt = tokenizer.encode("Write a summary of the new features in the latest release of the Julia Programming Language", return_tensors="pt")
generated = model.generate(prompt)

generated_text = tokenizer.decode(generated[0])
with open("generated.txt", "w") as f:
    f.write(generated_text)